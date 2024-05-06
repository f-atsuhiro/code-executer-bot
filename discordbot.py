
import discord
from os import getenv
import requests
from enum import Enum


client = discord.Client()
token = getenv('DISCORD_BOT_TOKEN')

class Language(Enum):
    cs = "dotnetcore-5.0.201"

def run_prog(lang : Language, code : str):
    parameter = dict(compiler = lang.value,code = code)
    try:
        response = requests.post("https://wandbox.org/api" + "/compile.json",json=parameter)
        if response.status_code != 200:
            print("wandbox error")

        r = response.json()

        stdout = ""
        
        if "program_message" in r:
            stdout += f"```\n{r['program_message']}```"
        if "compiler_message" in r:# and lang != Language.cs:
            stdcom = r['compiler_message'].split("\n")
            stdout += "```\n"
            for i in range(32,len(stdcom)):
                stdout += f"{stdcom[i]}\n"
            stdout += "```"
    except:pass
    return stdout

@client.event
async def on_message(msg):
    if msg.author.bot:#bot自身なら
        return
    space_msg = msg.content.split(" ")
    enter_msg = msg.content.split("\n")
    semicolon_msg = []
    for i in range(len(enter_msg)):
        semicolon_msg.append(enter_msg[i].split(";"))
    print(semicolon_msg)
    if space_msg[0] == "/help":
        await msg.channel.send("/exec\n```/exec <言語(py)>\n` ` `\n<コード>\n` ` `\n[in]\n` ` `\n[入力]\n` ` `\n\nコードと入力に対するprintを返します。\nまた、\"`\"どうしの間のスペースは不必要です。```")
    if space_msg[0] == "/exec":
        discord_output_msg_list = []
        if space_msg[1] == "help":
            await msg.channel.send("py\n```\nCpython 3.8.4\n\ninput関数及びprint関数の第一引数をサポートします(sys.stdin.readline()はサポートされません)。\nただし、これらの関数をオブジェクトとして扱う場合の動作は保障されません\n```\ncs\n```\n.NET CORE 5.0.201\n\n(wandboxを使用し実行します)\nReadLine及び全ての標準出力をサポートします```")
        # elif space_msg[1][0:3] == "cpp":
        #     i = 2
        #     if enter_msg[1] != "```" and enter_msg[1] != "```cpp":
        #         await msg.channel.send("コードはコードブロック内に記述してください。\nまた、コマンドとコードブロックの間にスペースを開けないでください")
        #         return
        #     program = ""
        #     while True:
        #         if semicolon_msg[i][0] == "```":
        #             break
        #         for j in range(len(semicolon_msg[i])):
        #             if "cin" in semicolon_msg[i][j]:
        #                 tmp_msg = semicolon_msg[i][j].split(">>")
        #             program += semicolon_msg[i][j]
        #             program += ";\n"
        #         i += 1
        #     print(program)
        elif space_msg[1][0:2] == "cs":
            i = 2
            if enter_msg[1] != "```" and enter_msg[1] != "```cs":
                await msg.channel.send("コードはコードブロック内に記述してください。\nまた、コマンドとコードブロックの間にスペースを開けないでください")
                return
            program = ""
            while True:
                if enter_msg[i] == "```":
                    break
                program += enter_msg[i]
                program += "\n"
                i += 1
            #プログラムが実行可能になった時点で次は入力を入れる。
            #コンマ区切りの入力strを作る
            i += 1
            discord_cs_in = ""
            try:
                if enter_msg[i] == "in":
                    i += 1
                    if enter_msg[i] != "```":
                        await msg.channel.send("入力はコードブロック内に記述してください。\nまた、inとコードブロックの間にスペースを開けないでください")
                        return
                    while True:
                        i += 1
                        if enter_msg[i] == "```":
                            break
                        discord_cs_in += "\"" + enter_msg[i] + "\""
                        discord_cs_in += ","
            except:pass#入力無し
            #最初のclass宣言を探し、直後の行にstatic public string[] discord_input_list = {コンマ区切りの入力str};\nstatic public int discord_input_counter = 0;
            for i in range(len(program) - 5):
                if program[i] == "c" and program[i + 1] == "l" and program[i + 2] == "a" and program[i + 3] == "s" and program[i + 4] == "s":
                    num = i + 5
                    while True:
                        if program[num] == "{":
                            program = program[:num + 1] + "\nstatic public string[] discord_input_list = {" + discord_cs_in + "};\nstatic public int discord_input_counter = 0;\nstatic public string Discord_Input_func(){\nstring str = discord_input_list[discord_input_counter];\ndiscord_input_counter++;\nreturn str;\n}" + program[num + 1:]
                            break
                        num += 1
                    break
            #次にSystem.Console.ReadLine();をdiscord_input_list[discord_input_counter];\ndiscord_input_counter ++;に置き換える
            program = program.replace("System.Console.ReadLine()","Discord_Input_func()")
            program = program.replace("Console.ReadLine()","Discord_Input_func()")
            program = program.replace("ReadLine()","Discord_Input_func()")
            print(program)

            discord_stdout = run_prog(Language.cs,program)
            print(discord_stdout)
            discord_stdout = discord_stdout.split("\n")
            discord_num_stdout = "```"
            for i in range(1,len(discord_stdout)):
                discord_line_char = str(i).ljust(5)
                discord_num_stdout += f"{discord_line_char}| {discord_stdout[i]}\n"
            if enter_msg[0] == "/exec cs --gc":
                discord_num_stdout += "生成されたコード\n"
                discord_num_stdout += "```\n" + program + "\n```"
            await msg.channel.send(discord_num_stdout)
        elif space_msg[1][0:2] == "py":
            program = "def discord_return_a_set_func():\n    global discord_output_msg_list\ndiscord_return_a_set_func()\n"
            #print(msg.content)
            if enter_msg[1] != "```" and enter_msg[1] != "```py":
                await msg.channel.send("コードはコードブロック内に記述してください。\nまた、コマンドとコードブロックの間にスペースを開けないでください")
                return
            i = 2
            while True:
                try:
                    #print(enter_msg[i],enter_msg[i] in "print(","print(" in enter_msg[i])
                    if enter_msg[i] == "```":
                        break
                    # if "import" in enter_msg[i] or "from" in enter_msg[i] or "open(":
                    #     if "collections" in enter_msg[i]:
                    #         pass
                    #     else:
                    #         await msg.channel.send("使用できない命令が含まれています。")
                    #         return
                    if "print(" in enter_msg[i]:
                        #print(enter_msg,"run_code")
                        enter_msg[i] = enter_msg[i][:-1]
                        enter_msg[i] += ",))"
                    program += enter_msg[i]
                    program += "\n"
                    if enter_msg[i][0:3] == "def":
                        for j in range(len(enter_msg[i + 1])):
                            if enter_msg[i + 1][j] == " ":
                                program += " "
                            else:
                                break
                        program += "global discord_output_msg_list,discord_input_list,discord_input_counter\n"
                    i += 1
                except:
                    await msg.channel.send("コードブロックは閉じてください。")
                    return
            program = program.replace("print(","discord_output_msg_list.append((")
            #ここにinput()をdiscordのIn項目に書かれたものを代入する処理を書く
            i += 1
            input_list = []
            watch_indent_line_counter = 4
            try:
                if enter_msg[i] == "in":
                    i += 1
                    if enter_msg[i] == "```":
                        i += 1
                        while True:
                            #try:
                                if enter_msg[i] == "```":
                                    break
                                input_list.append(f"{enter_msg[i]}")
                                #print(input_list)
                                find_input = program.find("input()")
                                program = program.replace("input()","discord_input_list[discord_input_counter]",1)
                                for j in range(find_input,len(program) - 1):
                                    if find_input == -1:
                                        break
                                    if program[j] == "\n":#どこで改行があるか(そのあとにカウンタ加算命令)
                                        for k in range(find_input,0,-1):#inputをみつけた場所から前に戻り改行を探す(その後インデントの数を見る)
                                            indent_break_flag = False
                                            if program[k] == "\n":
                                                indent_discord_in = ""
                                                #print(k,len(program),program[k])
                                                for l in range(k + 1,len(program)):
                                                    if program[l] == " ":
                                                        indent_discord_in += " "
                                                    else:
                                                        indent_break_flag = True
                                                        break
                                            else:
                                                continue
                                            if indent_break_flag:
                                                break
                                        program = program[:j + 1] + f"{indent_discord_in}discord_input_counter += 1\n" + program[j + 1:]
                                        watch_indent_line_counter += 1
                                        break
                                i += 1
                            #except : 
                            #    print("error")
                    else:
                        await msg.channel.send("入力はコードブロック内に記述してください。\nまた、inとコードブロックの間にスペースを開けないでください")
            except:pass
            program = f"\ndiscord_input_list = {input_list}" + "\ndiscord_input_counter = 0\n" + program
            print(program)
            try:
            #run_py(program)
                d = dict(locals(), **globals())
                exec(program,d,d)
            except:
                import traceback
                error = traceback.format_exc()
                error_list = error.split("\n")
                error_out = "```"
                error_out += "1\t| fail run code\n"
                for i in range(2,len(error_list) + 2):
                    error_out += f'{i}\t| {error_list[i - 2]}\n'
                error_out += "```"
                await msg.channel.send(error_out)
                return
            out = "```\n"
            discord_line_cnt = 0
            for i in range(len(discord_output_msg_list)):
                discord_line_cnt += 1
                discord_line_char = str(discord_line_cnt).ljust(5)
                out += f"{discord_line_char}| "
                print(discord_output_msg_list)
                if type(discord_output_msg_list[i]) is tuple:
                    for item in discord_output_msg_list[i]:
                        print(type(item))
                        while True:
                            if type(item) is not str:
                                print("break")
                                break
                            if item.find("\n") == -1:
                                break
                            discord_line_cnt += 1
                            discord_line_char = str(discord_line_cnt).ljust(5)
                            item = item.replace("\n",f"discord_enter_character_set_zone{discord_line_char}| ",1)
                        if type(item) is str:
                            item = item.replace(f"discord_enter_character_set_zone","\n")
                        out += f"{item} "
                else:
                    out += str(discord_output_msg_list[i])
                out += "\n"
            out += "```"
            if enter_msg[0] == "/exec py --gc":
                out += "\n生成されたコード\n```\n" + program + "\n```"
            await msg.channel.send(out)
            #print(program)
        else:
            await msg.channel.send("言語が指定されていない、あるいは未対応言語です。")

client.run(token)
