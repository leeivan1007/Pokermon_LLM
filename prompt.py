
api_key  = <Enter your openai key>
imgur_client_id = <Enter your imgur client id>


trick_prompt = """\
根據這張圖表的資訊，你應該使出哪一個招式？\
例如從上至下，招式表為：
TACKLE
GROWL
請一步一步的說明原因，並選擇招式，說明請限制在120字內。
假設你想使用GROWL，招式從上至下的排列為第2招，則請用文字表達->輸出：2\
以下為範例：
說明：GROWL對於戰鬥很有幫助...
輸出：2
"""

target = '訓練 BULBASAUR，讓它到達或者超過等級 6'

plan_prompt = """\
想像你是寶可夢大師 Red，你現在擁有一隻寶可夢叫 BULBASAUR，
目標：
1. {target}。如果完成了這個目標，請輸出[完成任務]
2. 確保它的健康狀態不低於 50%，如果低於50%，請輸出[規劃治癒]
3. 其餘狀況，訓練它直到完成目標1，請輸出[規劃戰鬥]

輸出格式：請用文字表示，輸出:(動作) 例如，輸出：規劃戰鬥

BULBASAUR 健康狀態：{healthy_state}
BULBASAUR 目前等級：{level}
"""