
import os,datetime
import pandas as pd
import json5 as json
import shutil
import win32clipboard
import pygetwindow as gw
import keyboard
import time
import utils.pyask as ask


class PwdMan():
    def __init__(self,datafile=None):

        self.this_window = gw.getActiveWindow()

        self.dir = os.path.dirname(os.path.realpath(__file__))

        if (datafile == None):
            datafile = os.path.join(self.dir,"Passwords.json")
        self.datafile = datafile

        self.data = self.load()

        # the columns in the first item ... this will be used as a template
        self.columns = list(self.data['0'].keys())

        self.Modes = {
            "f":{"name":"Find","fn":self.find},
            "g":{"name":"Get","fn":self.get},
            "a":{"name":"Add","fn":self.add},
            "e":{"name":"Edit","fn":self.edit},
            "s":{"name":"Save","fn":self.save},
            "q":{"name":"Quit","fn":self.quit},
        }


        self.main()

    def main(self):

        loop = True
        while loop:

            print("\nPick A Mode:")
            # for m in self.Modes:
            #     print(f"\t{m.code} | {m.name}")
            for k in self.Modes.keys():
                print(f"   {k} | {self.Modes[k]['name']}")
            
            user_input = input("")
            print(user_input)

            if user_input in self.Modes:
                self.Modes[user_input]['fn']()
            else:
                print("Invalid input. Please choose a valid option.")

    def find(self):

        print("\ntype to search:")
        user_input = ""
        backspace_count = 0
        while True:

            event = keyboard.read_event(suppress=True)

            # exit search if not the active window
            if self.this_window != gw.getActiveWindow():
                break

            if event.event_type == keyboard.KEY_DOWN:
                char = event.name

                if char == "shift":
                    continue

                if char == "enter" or char == "esc":
                    break  # Exit the loop if the user presses Enter
                elif char == "backspace":
                    user_input = user_input[:-1]  # Remove the last character on Backspace
                    backspace_count += 1
                else:
                    user_input += char
                    backspace_count = 0 

                if backspace_count >= 3:
                    backspace_count = 0 
                    user_input = ""
                
                # break for control C
                if user_input.endswith("ctrlc"):
                    break

                # filtered_result = filter_list(user_input, my_list)
                # filtered_result = [ f"{k} | {str(self.data[k])}" for k in self.data if user_input in str(self.data[k]).lower()]

                filtered_result = []
                for k in self.data:
                    if user_input not in str(self.data[k]).lower():
                        continue

                    fr = {"Id": k}
                    for c in self.data[k].keys():
                        fr[c] = self.data[k][c]
                    
                    filtered_result.append(fr)

                os.system('cls') 
                print("\n\n\n")
                print(f"{user_input}|")
                # print(*filtered_result[0:10],sep='\n')
                
                try:
                    temp = pd.DataFrame(filtered_result[0:10])
                    temp = temp.set_index("Id")
                    print(temp)
                except:
                    pass

                time.sleep(0.05)  # Optional delay to control the speed of updates

    def get(self):
        id = ask.ask("ID to Edit",int)
        key = ask.choose_one(choices=list(self.data[str(id)].keys()))
        self.copy_to_clipboard(self.data[str(id)][key])
        print(f"{key} was copied to clipboard")

    def edit(self):
        id = ask.ask("ID to Edit",int)
        key = ask.choose_one(choices=list(self.data[str(id)].keys()))
        currValue = self.data[str(id)][key]
        value = input("new Value:") or currValue
        self.data[str(id)][key] = value 
        print(f"updated: {self.data[str(id)]}")
        self.save()

    def add(self):
        nid = len(self.data)
        while (str(nid) in self.data.keys()):
            nid += 1
        
        new = {}
        for c in self.columns:
            new[c] = ask.ask(f"value for {c}:",str)
        
        self.data[str(nid)] = new
        print(f"new value: {str(new)}")
        self.save()

    def quit(self):
        print("Bye")
        quit()

    def copy_to_clipboard(self,text):
        try:
            win32clipboard.OpenClipboard()
            # win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        finally:
            win32clipboard.CloseClipboard()

    def load(self,default={}):
        try:
            with open(self.datafile,'r') as file:
                return json.load(file)
        except Exception as e:
            print(e)
            return default
    
    def save(self):

        # date = datetime.datetime.now().strftime('%Y%m%d_%H%M_%S')

        # one backup a say is all i need
        date = datetime.datetime.now().strftime('%Y%m%d')
        backup_datafile = self.datafile.replace('.json',f'{date}.json')

        shutil.copy2(self.datafile,backup_datafile)
        print(f"backup created: {backup_datafile}")

        with open(self.datafile,'w') as file:
            file.write(json.dumps(self.data,indent=4))
        
        print(f"Saved: {self.datafile}")
            


if __name__ == '__main__':
    PwdMan()
