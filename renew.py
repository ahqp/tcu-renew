from selenium import webdriver
import requests
import datetime
import time
import random
import json
import os
push_api_url = 'https://api.line.me/v2/bot/message/push'

#貸し出し中の資料がない場合の処理
#毎日見に行くなら、予約が入った時点で通知が欲しい

def line_push(line_user_id, messages):
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + line_token}
    data = {
        'to' : line_user_id,
        'messages' : [{'type':'text', 'text':m } for m in messages]
    }
    jsonstr = json.dumps(data)
    r = requests.post(push_api_url, data=jsonstr, headers=headers)
    return r

if __name__ == "__main__":
    line_token = os.environ["LINE_TOKEN"]
    line_user_id = os.environ["LINE_USER_ID"]
    tcu_user_id = os.environ["TCU_USER_ID"]
    tcu_password = os.environ["TCU_PASSWORD"]

    login_url = "https://www.lib.tcu.ac.jp/webopac/opacsnd.do?opac_target=lenlst.do&locale=ja"

    options = webdriver.ChromeOptions()
    #options.binary_location = '/app/.apt/usr/bin/google-chrome'
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    time.sleep(5+(random.random()*5))
    #longin ユーザーネームとパスワードを保存
    driver.get(login_url)
    userid_form = driver.find_element_by_name("userid")
    userid_form.send_keys(tcu_user_id)
    password_form = driver.find_element_by_name("password")
    password_form.send_keys(tcu_password)
    driver.execute_script("JavaScript:submitFlag=true;opacSubmit();")
    time.sleep(5+(random.random()*5))

    #今日が返却期限の本にチェックを入れる
    table = driver.find_element_by_xpath("//table[@class='opac_data_list_ex']")
    num_renew = 0
    for row in table.find_elements_by_xpath(".//tr")[1:]:
        #貸し出し期限
        deadline_str = row.find_element_by_xpath(".//td[5]").text
        deadline_date = datetime.datetime.strptime(deadline_str, '%Y/%m/%d').date()
        today = datetime.date.today()
        #動作テスト用
        #today = datetime.date(2018, 12, 19)
        #返却期限が今日の資料にチェックを入れる
        #この時点で予約が入ってる資料、更新回数が上限の3回を超えてる資料は対象から排除し、メッセージを生成できるが、わざと更新処理して貸し出し失敗メッセージをサーバからもらった方がコードがしんぷるになうるのでそうする。
        if deadline_date == today:
            #チェックボックスクリック
            td_checkbox = row.find_element_by_xpath(".//td[2]")
            td_checkbox.find_element_by_name('lenidlist').click()
            num_renew += 1
    #今日が返却期限の本があったら貸し出し更新
    if 0 < num_renew:
        time.sleep(5+(random.random()*5))
        driver.execute_script("lenUpdt();return false;")
        alert = driver.switch_to.alert.accept()
        descriptions = driver.find_elements_by_class_name('opac_description_area')
        descriptions.pop(0)
        for i in range(len(descriptions)):
            line_push(line_user_id, [descriptions[i].text])
            lenupd_table = driver.find_elements_by_xpath("//table[@class='opac_data_list_ex']")[i]
            #貸出更新した資料一覧
            tr = lenupd_table.find_elements_by_xpath(".//tr")[1:]
            td = [i.find_elements_by_xpath(".//td") for i in tr]
            if len(td[0]) == 6:
                #更新に成功した資料
                #返却期限日と書誌事項
                line_push(line_user_id, [row[3].text + '\n' + row[5].text for row in td])
            elif len(td[0]) == 7:
                #更新に失敗した資料
                #原因と書誌事項
                line_push(line_user_id, [row[2].text + '\n' + row[6].text for row in td])
    else:
        pass
        #line_push(line_user_id, ['今日が返却期限の資料はありませんでした'])
    driver.quit()
