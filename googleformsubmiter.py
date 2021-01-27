import requests
import requests_html
import ast
import urllib
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from random import randint
import sys


def main(url = None):
    console = Console()


    session = requests_html.HTMLSession()

    if url == None: url = Prompt.ask("Enter the google form url")

    url_parse = urllib.parse.urlparse(url)
    if (url_parse.scheme == "" or url_parse.netloc == ""):
        console.log("red bold]ERROR[/red bold] Invalid url.")
        return 


    with console.status("[bold green]Retriving google form...") as status:
        try :
            r = session.get(url) 
            if (r.status_code != 200): raise Exception("Invalid url, error code "+str(r.status_code))
        except Exception as e:
            console.log("[red bold]ERROR[/red bold] Invalid url, can't retrived google form. (error: "+str(e)+")")
            return
        else :
            console.log("Google form retrived.")
        
    with console.status("[bold green]Parsing questions...") as status:
        try:
            items = r.html.find(".freebirdFormviewerViewNumberedItemContainer")
            qr = []

            for item in items:
                t = item.find('.m2', first=True)
                a =  ast.literal_eval(("["+t.attrs.get("data-params")[4:]).replace("null", "0").replace("false", "False").replace("true", "True"))
                e = [a[0][1], a[0][4][0][0], []]
                for el in a[0][4][0][1]:
                    e[2].append(el[0])
                qr.append(e)
        except Exception as e:
            console.log("[red bold]ERROR[/red bold] error while parsing questions : "+str(e))
            return
        else:
            console.log("Questions parsed.")

    console.print("\n")

    rep = {}

    for i, question in enumerate(qr):
        console.print(Panel(Columns([str(j+1) + ". "+question[2][j] for j in range(len(question[2]))]), title="Question "+str(i+1)+" : "+question[0]))
        while True:    
            ans = IntPrompt.ask("Response", default=randint(1, len(question[2])))
            if ans >= 1 and ans <= len(question[2]):
                break
            console.print("[prompt.invalid]Choice bewteen 1 and"+ len(question[2]))
        rep['entry.'+str(question[1])] = urllib.parse.quote_plus(question[2][ans-1])
        console.print("\n")

    n = IntPrompt.ask("Number of response : ", default=1)
    if n > 100: n = 100

    with console.status("[bold green]Sending responses...") as status:
        try:
            for i in range(n):
                r = requests.post(url.replace("viewform", "formResponse"), headers={"content-type":"application/x-www-form-urlencoded"}, data = rep)        
                console.log(str(i+1)+" responses sended.")
        except Exception as e:
            console.log("[bold red]ERROR[/bold red] Something wrong happend during sending : "+str(e))
            return

    console.print("\nbye")

if (__name__ == "__main__"):
    if (len(sys.argv) > 1):
        main(sys.argv[1])
    else: main()