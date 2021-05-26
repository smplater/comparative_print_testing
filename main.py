import requests 
import pandas as pd 

import time
import calendar

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os 

gmt = time.gmtime()
ts = calendar.timegm(gmt)

out_folder = rf"out/test_{ts}/"
out_dir= os.getcwd() + r"/" + out_folder
os.mkdir(out_dir)

options = webdriver.ChromeOptions() 
options.headless = True 
columns_report_frame = ['test_case', 'user', 'comparison', 'completed_test_ts', 'outcome_img', 'outcome_analysis']
rf = pd.DataFrame(columns=columns_report_frame)


def reportID(df): 
    return df.bill_a_session + df.bill_a_type + df.bill_a_num  + df.bill_a_stage + "-" + df.bill_b_session + df.bill_b_type + df.bill_b_num  + df.bill_b_stage + '-compare'

df = pd.read_csv(r'tests.csv')
df = df.astype(str)
df['reportId'] = df.apply(reportID, axis=1)
df['test_image'] = None
df['_url'] = None

for i, r in df.loc[:,"tab":].iterrows():

    # parameters to run test
    if df.user[i] == 'basic': 
        break
    elif df.case_type[i] == 'upload': 
        break
    else: 
        pass

    # params for test 
    params = {x:r[i] for i, x in enumerate(r.index)}
    r = requests.get(df.url[i], params)
    driver = webdriver.Chrome('./chromedriver', options=options)

    # test begins
    driver.get(r.url)

    print(f"\t waiting for {df.reportId[i]} to load")
    print(f"full url: {r.url}")
    time.sleep(30) # allows for load time

    # loading has bene performed
    # assume live web page

    # gets width of the doc 
    s = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X) 
    w = s('Width') 
    driver.set_window_size(w-1, 5000)

    print(f"\t getting screenshot for {df.reportId[i]}")
    images_path = f"{out_folder}/_{ts}_results_{i}.png"
    images_path_a = f"{out_folder}/_{ts}_results_a_{i}.png"
    driver.find_element_by_tag_name('body').screenshot(images_path)

    compPrintTab = driver.find_element_by_partial_link_text("Comparative Print")
    compPrintTab.click()
    time.sleep(5)
    driver.save_screenshot(images_path_a)


    driver.close()

    rs = pd.Series( 
            {'url':r.url,
            'user':df.user[i], 
            'comparison':df.reportId[i].replace("-","_"),
            'completed_test_ts':str(ts),
            'outcome_analysis':'',
            'outcome_result_pf':''}, 
            name=i
            )

    rf = rf.append(rs)

    print('\n\n')

rf['test_case'] = rf.index
rf = rf[['url', 'user', 'comparison', 'completed_test_ts', 'test_case', 'outcome_result_pf', 'outcome_analysis']]


rf.to_csv(rf"{out_folder}/_{ts}_results.csv", index=False)
