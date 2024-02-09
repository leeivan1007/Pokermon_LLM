# %%
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import pyimgur
import copy
from openai import OpenAI
from prompt import *
import re

client = OpenAI(api_key=api_key)
pyboy = PyBoy('Pokemon Red.gb', game_wrapper=True)
pyboy.set_emulation_speed(4.0)

def read_hp( start):
    return 256 * read_m(start) + read_m(start+1)
def read_m(addr):
    return pyboy.get_memory_value(addr)
def upload_image(path):
    im = pyimgur.Imgur(imgur_client_id)
    image_url = im.upload_image(path, title="test")
    return image_url
def choice_tricks(url):
    
    while True:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": trick_prompt},
                        {
                            "type": "image_url",
                            "image_url": f"{url}",
                        },
                    ],
                }
            ],
            max_tokens=400,
            temperature=0.0,
        )
        
        result = response.choices[0].message.content
        if '輸出：' in result:
            break
        else:
            print('招式讀取失敗')

    return result
def get_trick_index(message):
    
    result = re.search(r"輸出：(\d+)", message)
    paragraph, trick_index = str(result.group(0)), int(result.group(1))
    
    return trick_index, paragraph
def plan_action(healthy_state, level, target):
    input_message = plan_prompt.format(healthy_state=healthy_state, level=level, target=target)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": input_message,
            }
        ],
        max_tokens=400,
        temperature=0.0,
    )
    return response.choices[0].message.content

class GameBoy():
    def __init__(self, pyboy):
        self.pyboy = pyboy
        self.mode = 'practice_mode' # navigation_mode
        self.tasks = []
        self.return_trajectory = []
        self.practice_area = [(0,1), (0,1), (0,1), (0,1), (0,1), (3,1),
                             (1,1), (1,1), (1,1), (1,1), (1,1), (2,1)]
        self.current_pos = ()
        self.battle_screen_path = 'battle.png'
        self.current_index = 1
    def down(self):
        self.pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN)
        for i in range(24):
            if i == 8:
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_DOWN)

            self.pyboy.tick()
    def left(self):
        self.pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
        for i in range(24):
            if i == 8:
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)

            self.pyboy.tick()
    def up(self):
        self.pyboy.send_input(WindowEvent.PRESS_ARROW_UP)
        for i in range(24):
            if i == 8:
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_UP)

            self.pyboy.tick()
    def right(self):
        self.pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
        for i in range(24):
            if i == 8:
                self.pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)

            self.pyboy.tick()
    def move(self, direct, time):
        for _ in range(time):
            if direct == 0:
                self.up()
            elif direct == 1:
                self.down()
            elif direct == 2:
                self.left()
            elif direct == 3:
                self.right()
    def press_button_A(self):
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_A)
        for i in range(300):
            if i == 8:
                self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)

            self.pyboy.tick()
    def press_button_B(self):
        self.pyboy.send_input(WindowEvent.PRESS_BUTTON_B)
        for i in range(24):
            if i == 8:
                self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_B)

            self.pyboy.tick()
    def wait_time(self, time):
        for _ in range(time):
            self.pyboy.tick()
    def plan_trajectory(self, trajectory):
        for t in trajectory:
            if type(t) == tuple:
                self.move(t[0], t[1])
            elif type(t) == int:
                self.wait_time(t)
            elif 'A' in t:
                for _ in range(len(t)):
                    self.press_button_A()
            elif 'B' in t:
                for _ in range(len(t)):
                    self.press_button_B()    
    def read_m(self, addr):
        return self.pyboy.get_memory_value(addr)
    def get_position(self):
        x_position = self.read_m(0xD362)
        y_position = self.read_m(0xD361)
        return x_position, y_position
    def solve_tasks(self):
        for task in self.tasks:
            pass
    def execute_task(self, task):
        if task == 'arrive_pratice_area':
            trajectory = [(0,1)]
            self.plan_trajectory(trajectory)
            self.return_trajectory.append((1,1))
        if task == 'cruising_mode':
            trajectory = copy.deepcopy(self.practice_area)
            self.plan_trajectory(trajectory)
    def get_hps(self):
        enemy_hp = [self.read_m(addr) for addr in [0xCFE6, 0xCFE7]]
        ours_hp = [self.read_m(addr) for addr in [0xD015, 0xD016]]
        return enemy_hp, ours_hp
    def save_image(self):
        image = self.pyboy.screen_image()
        image.save(self.battle_screen_path)
    def action_trick(self, trick_index):
        if self.current_index == trick_index:
            self.plan_trajectory(['A'])
        elif self.current_index > trick_index:
            self.plan_trajectory([(0, self.current_index-trick_index), 'A'])
        elif self.current_index < trick_index:
            self.plan_trajectory([(1, trick_index-self.current_index), 'A'])
        self.current_index = trick_index
                            
gameboy = GameBoy(pyboy)
trajectory = ['A'*7] 
gameboy.plan_trajectory(trajectory)

# %%
dead_state = False
while True:
      if dead_state:
            gameboy.plan_trajectory([(3,5), (0,4)])
            dead_state = False
      hp = read_m(0xD16D)
      full_hp = read_m(0xD18E)
      healthy_state =  f'{int((hp / full_hp) * 100)}%'
      level = read_m(0xD18C)

      action = plan_action(healthy_state, level, target)
      print(f'血量：{hp} | 總血量：{full_hp} | 健康狀況：{healthy_state} | 等級：{level} | 規劃：{action}')

      if action == '規劃戰鬥':

            pratice_area = [(0,1),(0,1), (0,1), (0,1), (0,1), (0,1), (3,1),
                  (1,1), (1,1), (1,1), (1,1), (1,1),(1,1), (2,1)]
            times = 0

            for step in pratice_area:
                  
                  if dead_state: break
                  gameboy.plan_trajectory([step])
                  new_position = gameboy.get_position()
                  
                  while gameboy.current_pos == new_position and times < 2:
                        gameboy.plan_trajectory([step])
                        gameboy.current_pos = gameboy.get_position()
                        times += 1
                        
                  if gameboy.current_pos == new_position and times == 2:
                        gameboy.current_index = 1
                        gameboy.plan_trajectory([500, 'B', 200, 'B', 'A'])
                        
                        enemy_hp, ours_hp = gameboy.get_hps()
                        while enemy_hp != [0,0]:
                              
                              gameboy.save_image()
                              
                              # trick_index = 1
                              image_url = upload_image(gameboy.battle_screen_path)
                              llm_message = choice_tricks(image_url.link)
                              print(llm_message)
                              trick_index, paragraph = get_trick_index(llm_message)
                              
                              gameboy.action_trick(trick_index)
                              gameboy.plan_trajectory(['B', 200,'B', 200,'B', 100, 'A'])
                              enemy_hp, ours_hp = gameboy.get_hps()
                              
                              if gameboy.get_position() == (5, 6):
                                    dead_state = True
                                    break
                              
                        for _ in range(2):
                              gameboy.plan_trajectory(['B', 100])
                        gameboy.plan_trajectory([step])
                        times = 0

                  elif gameboy.current_pos != new_position:
                        gameboy.current_pos = gameboy.get_position()

      elif action == '規劃治癒':
            
            trajectory = [(1,4), (2,5), (0,1), 300] # 去家
            trajectory += [(3,3), (0,2), 'A'*7] # 找媽
            trajectory += [(1,2), (2,3), (1,1), 300] # 離媽
            trajectory += [(3,5), (0,4)] # 離家

            gameboy.plan_trajectory(trajectory)
            
      elif action == '完成任務':
            print('任務完成！')
            break


# %%
gameboy.pyboy.stop()

# %%



