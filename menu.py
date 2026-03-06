def menu(
    header: str, 
    posibilities: list[str], 
    pickText: str, 
    retryTexts: str
):
    if len(posibilities) == 0:
        quit()

    userInput = False
    while not userInput:
        print(header)
        print()
        
        for index, posibilitie in enumerate(posibilities):
            print(f"{index+1}) {posibilitie}")

        print()
        userInput = str(input(pickText))

        try:
            if userInput in posibilities:
                print()
                return userInput
            
            pick = int(userInput)
            if pick > 0 or pick <= len(posibilities):
                print()
                return posibilities[pick-1]
            
            print(retryTexts)
        except:
            print(retryTexts)

        print()
        waitEnter()
        print()

        userInput = False

def waitEnter(text: str = '...'):
    waiting = str(input(text))