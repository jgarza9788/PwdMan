
import os,time,datetime
import pandas as pd
import shutil
import win32clipboard
import pygetwindow as gw
import keyboard
import utils.pyask as ask
from fuzzywuzzy import process

#use rich
from rich.console import Console
from rich.table import Table
print = Console().print

class PwdMan():
    def __init__(self,
                 datafile=None
                 ):

        self.this_window = gw.getActiveWindow()

        self.dir = os.path.dirname(os.path.realpath(__file__))

        if (datafile == None):
            datafile = os.path.join(self.dir,"Passwords.csv")
        self.datafile = datafile

        self.data = self.load()
        self.filtered_data = None

        # the columns in the first item ... this will be used as a template
        # self.columns = list(self.data['0'].keys())
        self.show_disabled = False

        # dfl = [ r for r in self.data.reset_index().to_dict(orient='records')]
        # print(dfl)

        self.main()

    def find_best_matches(self,query, dataframe):
        best_matches = []


        dfl = [ (r['index'],str(r).lower()) for r in dataframe.to_dict(orient='records')]
        # print(dfl)

        # Use fuzzywuzzy to get a list of tuples (row_index, similarity_score)
        matches = process.extractBests(query, dfl, score_cutoff=45,limit=1000)
        print(matches)
        
        if len(matches) <= 0:
            return []
        
        # Extract the row indices from the tuples
        matched_indices = [match[0][0] for match in matches]
        
        # Return the DataFrame with the best matching rows
        return dataframe.loc[matched_indices]

    def main(self):

        loop = True
        while loop:

            options = {
                "f":{"name":"Find","fn":self.find},
                "g":{"name":"Get","fn":self.get},
                "a":{"name":"Add","fn":self.add},
                "e":{"name":"Edit","fn":self.edit},
                "p":{"name":"Print","fn":self.print},
                "t":{"name":f"Toggle show_disabled= {self.show_disabled}","fn":self.toggle_show_disabled},
                "d":{"name":"Delete","fn":self.delete},
                "s":{"name":"Save","fn":self.save},
                "b":{"name":"BackUp","fn":self.backup},
                "q":{"name":"Quit","fn":self.quit},
                # "tt":{"name":"run a test function","fn":self.test},
            }

            print("\nPick A Mode:")
            # for m in self.Modes:
            #     print(f"\t{m.code} | {m.name}")
            for k in options.keys():
                print(f" {k} | {options[k]['name']}")
            
            user_input = input("")
            # print(user_input)

            if user_input in options:
               options[user_input]['fn']()
            else:
                print("Invalid input. Please choose a valid option.")

    def find(self):
        os.system('cls') 
        print("\ntype to search:")
        print("|")
        # print(type(self.filtered_data).__name__)
        # print(type(self.data).__name__)
        if type(self.filtered_data).__name__ == "DataFrame":
            # print(self.filtered_data.head(10))
            self.show_filtered_data()

        self.filtered_data = None
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
                elif char == "delete":
                    user_input = ""
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

                temp_data = None
                if self.show_disabled:
                    temp_data = self.data.reset_index()
                else:
                    temp_data = self.data.reset_index().query('not notes.str.contains("disabled")', engine='python')

                filtered_result = []
                for r in temp_data.to_dict(orient='records'):
                    if user_input not in str(r).lower():
                        continue
                    # print(r)
                    filtered_result.append(r)
                filtered_result = pd.DataFrame(filtered_result)

                # this is a smart filter using the fuzzy search, but it takes too long
                # filtered_result = self.find_best_matches(user_input,temp_data)

                if len(filtered_result) > 0:
                    filtered_result.set_index('index',inplace=True)


                os.system('cls') 

                
                print("\ntype to search:")
                print(f"{user_input}|")
                # print(*filtered_result[0:10],sep='\n')
                
                try:
                    self.filtered_data = filtered_result
                    # print(filtered_result.head(20))
                    # self.pd_rich_table(filtered_result.head(20))
                    self.show_filtered_data()
                except:
                    pass

                # time.sleep(0.05)  # Optional delay to control the speed of updates

    # def test(self):
    #     self.pd_rich_table(self.data)

    def pd_rich_table(self,df):
        # convert the index
        tdf = df.reset_index().copy()

        table = Table()

        colors = ['white','cyan','magenta','green','purple','red']

        for index,col in enumerate(list(tdf.columns)):
            # print(col)
            table.add_column(col, justify="right", style=colors[index%len(colors)], no_wrap=True,max_width=25)
        
        # print(tdf.to_dict(orient='split'))

        for i in tdf.to_dict(orient='split')['data']:
            # print(i.tolist())
            # print(i,type(i))
            # print(type(i))
            # for j in in i:
            # ii = [str(j) for j in i]
            # print(ii)
            # table.add_row(*ii)
            table.add_row(*[str(j) for j in i])

        print(table)

    def toggle_show_disabled(self):
        if self.show_disabled  == True:
            self.show_disabled = False
        else:
            self.show_disabled = True
        print(f'show disabled: {self.show_disabled}')

    def show_filtered_data(self):
        if type(self.filtered_data).__name__ == "DataFrame":
            # print(self.filtered_data.head(20))
            self.pd_rich_table(self.filtered_data.head(20))
        print("")

    def get(self):
        self.show_filtered_data()

        if len(self.filtered_data) == 1:
            index = self.filtered_data.index[0]
        else:
            index = ask.ask("Index to get: ",int)

        if index == None:
            return 0

        col = ask.choose_one(choices=list(self.data.columns))
        if col == None:
            return 0
        value = str(self.data.loc[index, col])

        self.copy_to_clipboard(value)
        print(f"\"{value}\" was copied to clipboard")

    def edit(self):
        self.show_filtered_data()

        if len(self.filtered_data) == 1:
            index = self.filtered_data.index[0]
        else:
            index = ask.ask("index to Edit: ",int)

        if index == None:
            return 0
        
        col = ask.choose_one(choices=list(self.data.columns))
        if col == None:
            return 0

        currValue = str(self.data.loc[index, col])
        value = ask.ask("new Value:",str) or currValue
        self.data.at[index,col] = value 
        print(f"updated: \n{self.data.loc[index,:]}")
        self.save()

    def print(self):
        self.show_filtered_data()

        if len(self.filtered_data) == 1:
            index = self.filtered_data.index[0]
        else:
            index = ask.ask("Index to get: ",int)

        if index == None:
            return 0
        
        print(self.data.loc[index,:])


    def add(self):
        new = {}
        for c in self.data.columns:
            value = ask.ask(f"value for {c}:",str) or ""
            if value == None:
                return 0
            new[c] = value
        
        index = len(self.data)
        ndf = pd.DataFrame(new,index=[index])
        self.data = pd.concat([self.data,ndf])

        self.save()
        
    def delete(self):
        index = ask.ask("index to Delete: ",int)

        if index == None:
            return 0

        item = self.data.loc[index,:]
        self.data = self.data.drop(index=index)

        self.save()
        print('the following was deleted')
        print(item)

    def quit(self):
        os.system('cls')
        print("Bye")
        quit()

    def copy_to_clipboard(self,text):
        try:
            win32clipboard.OpenClipboard()
            # win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        finally:
            win32clipboard.CloseClipboard()

    def backup(self):
        # date = datetime.datetime.now().strftime('%Y%m%d_%H%M_%S')
        date = datetime.datetime.now().strftime('%Y%m%d')
        backup_datafile = self.datafile.replace('.csv',f'_{date}.csv')
        shutil.copy2(self.datafile,backup_datafile)
        print(f"Saved: {backup_datafile}")

    def load(self,default={}):
        try:
            df = pd.read_csv(self.datafile).fillna("")
            return df
        except Exception as e:
            print(e)
    
    def save(self):
        self.data.to_csv(self.datafile,index=False)
        print(f"Saved: {self.datafile}")

        # date = datetime.datetime.now().strftime('%Y%m%d_%H%M_%S')

        # # one backup a say is all i need
        # date = datetime.datetime.now().strftime('%Y%m%d')
        # backup_datafile = self.datafile.replace('.json',f'{date}.json')

        # shutil.copy2(self.datafile,backup_datafile)
        # print(f"backup created: {backup_datafile}")

        # with open(self.datafile,'w') as file:
        #     file.write(json.dumps(self.data,indent=4))
        
        # print(f"Saved: {self.datafile}")
            


if __name__ == '__main__':
    PwdMan(datafile=r"D:\Documents\Passwords.csv")
