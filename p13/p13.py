from collections import defaultdict
import numpy as np
from matplotlib import pyplot as plt
import msvcrt
import pickle
class program():
    def __init__(self, code):
        self.pos = 0 # position pointer
        self.code = defaultdict(lambda:0)
        for i,v in enumerate(code):
            self.code[i] = v
        self.rel = 0 # offset value for relative mode
        self.inputs = []
        
    def add_inputs(self,inputs):
        for i in inputs:
            self.inputs.insert(0,i)
    
    def run(self):
        exit_code = 0
        outputs = []
        while exit_code == 0:
            exit_code, output = self._step()
            if output is not None:
                outputs.append(output)
        return exit_code, outputs
    
    def _parse_opcode(self, opcode):
        """
        Parse an opcode, getting the parameter modes and instruction.
        Opcode should be input as integer.
        """
        code = str(opcode)
        l = len(code)
        inst = int(code[-2:])
        modes = []
        for i in range(l-2):
            modes.append(int(code[l-3-i]))
        return inst, modes
    
    def _get_val_idx(self,loc,mode):
        if mode==0: # position mode
            return self.code[loc]
        elif mode==1: # immediate mode
            return loc
        elif mode==2: # relative mode
            return self.rel+self.code[loc]
        
    def _step(self):
        """
        Exit codes: 
           0 : continue execution
           1 : program finished
           2 : waiting for input
        """
        output = None
        exit_code = 0
        pos = self.pos # where are we in the code

        inst, modes = self._parse_opcode(self.code[pos])
        if inst == 99: # terminate
            exit_code = 1
            
        if inst == 1: # add
            modes = modes+(3-len(modes))*[0]
            v1 = self.code[self._get_val_idx(pos+1,modes[0])]
            v2 = self.code[self._get_val_idx(pos+2,modes[1])]
            self.code[self._get_val_idx(pos+3,modes[2])] = v1+v2 
            pos += 4
            
        if inst == 2: # multiply
            modes = modes+(3-len(modes))*[0]
            v1 = self.code[self._get_val_idx(pos+1,modes[0])]
            v2 = self.code[self._get_val_idx(pos+2,modes[1])]
            self.code[self._get_val_idx(pos+3,modes[2])] = v1*v2 
            pos += 4
            
        if inst == 3: # store input
            try:
                modes = modes + (1-len(modes))*[0]
                self.code[self._get_val_idx(pos+1,modes[0])] = self.inputs.pop()
                pos += 2
            except IndexError: # must wait for additional input
                exit_code = 2
                
        if inst == 4: # output value
            modes = modes+(1-len(modes))*[0]
            v = self.code[self._get_val_idx(pos+1,modes[0])]
            output = v
            pos += 2
            
        if inst == 5: # jump-if-true
            modes = modes+(2-len(modes))*[0]
            v1 = self.code[self._get_val_idx(pos+1,modes[0])]
            v2 = self.code[self._get_val_idx(pos+2,modes[1])]
            if v1 > 0:
                pos = v2
            else:
                pos += 3
                
        if inst == 6: # jump-if-false
            modes = modes+(2-len(modes))*[0]
            v1 = self.code[self._get_val_idx(pos+1,modes[0])]
            v2 = self.code[self._get_val_idx(pos+2,modes[1])]
            if v1 == 0:
                pos = v2
            else:
                pos += 3
                
        if inst == 7:
            modes = modes+(3-len(modes))*[0]
            v1 = self.code[self._get_val_idx(pos+1,modes[0])]
            v2 = self.code[self._get_val_idx(pos+2,modes[1])]
            if v1 < v2:
                self.code[self._get_val_idx(pos+3,modes[2])] = 1
            else:
                self.code[self._get_val_idx(pos+3,modes[2])] = 0
            pos += 4
            
        if inst == 8:
            modes = modes+(3-len(modes))*[0]
            v1 = self.code[self._get_val_idx(pos+1,modes[0])]
            v2 = self.code[self._get_val_idx(pos+2,modes[1])]
            if v1 == v2:
                self.code[self._get_val_idx(pos+3,modes[2])] = 1
            else:
                self.code[self._get_val_idx(pos+3,modes[2])] = 0
            pos += 4
            
        if inst == 9: # adjust rel
            modes = modes+(1-len(modes))*[0]
            v1 = self.code[self._get_val_idx(pos+1,modes[0])]
            self.rel += v1
            pos += 2
        self.pos = pos
        return exit_code, output
    
class arcade_cabinet():
    def __init__(self,code):
        self.prog = program(code)
        self.board = np.zeros((26,40),dtype=np.int)
        self.score = 0
        self.render_symbols = ["  ","==","[]","--","()"]
        self.moves = defaultdict(lambda:0,{"a":-1,"d":1,"j":-1,"l":1,u"\u2192":1,u"\u2190":-1})
        
    def load_game(self,fname):
        with open(fname,"r") as f:
            self.prog.pos = int(f.readline().strip())
            saved_code = [int(c) for c in f.readline().strip().split(",")]
            self.prog.code = defaultdict(lambda:0)
            for i,c in enumerate(saved_code):
                self.prog.code[i] = c
            self.prog.rel = int(f.readline().strip())
            l = f.readline().strip().split(",")
            if l[0] == "":
                self.prog.inputs = []
            else:
                self.prog.inputs = [int(c) for c in l]
            self.board = np.array([int(c) for c in f.readline().strip().split(",")],dtype=np.int).reshape((26,40))
            self.score = int(f.readline().strip())
    
    def render_board(self):
        """
        Create a string rendering of the game board.
        """
        board_string = ""
        for i in range(self.board.shape[0]):
            for j in range(self.board.shape[1]):
                board_string += self.render_symbols[self.board[i,j]]
            board_string += "\n"
        return board_string+"\nCurrent Score: {}".format(self.score)
    
    def run_program(self,render=False):
        render_flag = False
        while True:
            outputs = []
            while len(outputs) < 3:
                exit_code, output = self.prog._step()
                if exit_code == 1: # program halts
                    return
                if exit_code == 2: # needs input
                    if not render_flag:
                        print(self.render_board())
                        render_flag = True
                    move = msvcrt.getwch()
                    if move == "q":
                        print("saving")
                        with open("saved_game.txt","w") as f:
                            f.write(str(self.prog.pos)+"\n")
                            f.write(",".join([str(c) for c in self.prog.code.values()]) + "\n")
                            f.write(str(self.prog.rel)+"\n")
                            f.write(",".join([str(c) for c in self.prog.inputs])+"\n")
                            f.write(",".join([str(c) for c in self.board.flatten()])+"\n")
                            f.write(str(self.score))
                        move = msvcrt.getwch()
                    self.prog.add_inputs([self.moves[move]])
                if output is not None:
                    outputs.append(output)
            if outputs[0] == -1:
                self.score = outputs[2]
            else:
                self.board[outputs[1],outputs[0]] = outputs[2]
            if render and render_flag:
                print(self.render_board())
            
load_game = input("Load game? (y/n)")
if load_game == "y":
    save_file = input("enter filename: ")
    arcade = arcade_cabinet([])
    arcade.load_game(save_file)
    print(len(arcade.prog.code))
    
else:
    with open("p13_input.txt","r") as f:
        code = [int(c) for c in f.readline().strip().split(",")]
    code[0] = 2
    arcade = arcade_cabinet(code)
arcade.run_program(render=True)