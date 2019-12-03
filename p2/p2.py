def intcode(code):
    """
    Execute the instructions given in the input code. 
    Output the resulting state.
    """
    pos = 0
    while True:
        if code[pos] == 99: # terminate
            break
        else:
            codeblock = code[pos:pos+4]
            if codeblock[0] == 1: # add
                code[codeblock[-1]] = code[codeblock[1]] + code[codeblock[2]]
            if codeblock[0] == 2: # multiply
                code[codeblock[-1]] = code[codeblock[1]]*code[codeblock[2]]
        pos += 4
    return code

# part 1
with open("p2_input.txt","r") as f:
    incode = [int(c) for c in f.readline().split(",")]
incode[1] = 12
incode[2] = 2
print("Part 1 answer: {}".format(intcode(incode)[0]))


# part 2
for noun in range(100):
    for verb in range(100):
        with open("p2_input.txt","r") as f:
            incode = [int(c) for c in f.readline().split(",")]
        incode[1] = noun
        incode[2] = verb
        val = intcode(incode)[0]
        if val == 19690720:
            print("Part 2 answer: {}".format(100*noun + verb))
            break