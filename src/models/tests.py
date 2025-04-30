
def test1_openai_test() -> None :
    # model_name = 'gpt-3.5-turbo'
    # model_name = 'o4-mini'
    # model_name = 'o1-mini'
    model_name = 'gpt-4o-2024-11-20'
    # model_name = 'o1'
    # model_name = 'gpt-4'
    oaim = OpenAIModel(model_name=model_name)
    print(oaim.model_name)
    print(oaim.query(messages=[
        {
            'role': 'user',
            'content': 'what\'s the best way to bake a baguette? can you give me a series of instructions?'
        }
    ]))
    

def test2_replicate_llama_4_test() -> None :
    input = {
        "prompt": "Hello, Llama!"
    }

    output = []
    for event in replicate.stream(
        "meta/llama-4-maverick-instruct",
        input=input
    ):
        print(event, end="")
        output.append(event)
    
    print()
    # print(output)
    print("---".join([str(x) for x in output]))

    # for x in output :
        # print(str(x))
        # print(f'{type(x) = }')


from models import ModelManager
def test3_model_manager_test() -> None :
    mm = ModelManager()
    mm.add_character("test", "gpt-4")
    mm.add_character("test2", "o4-mini")
    mm.add_character("test3", "o1-mini")
    
    input1 = "Hi gpt-4o! What's the best place to visit during the summer in Europe?"
    output1 = mm.query_character("test", input1)
    print(f"Input1: {input1}")
    print(f"Output1: {output1}")
    print()
    
    input2 = "Hi o4-mini! What's the best place to visit during the summer in Asia? I'm a swimmer and hiker!"
    output2 = mm.query_character("test2", input2)
    print(f"Input2: {input2}")
    print(f"Output2: {output2}")
    print()
    
    input3 = "Hi o1-mini! What's the best place to visit during the summer in North America? I'm a jazz musician!"
    output3 = mm.query_character("test3", input3)
    print(f"Input3: {input3}")
    print(f"Output3: {output3}")
    print()
    
    print(f'Character list:')
    print(mm.get_character_list_str())
    
    



def main() -> None :
    test3_model_manager_test()
    
    
    pass


if __name__ == "__main__":
    main()