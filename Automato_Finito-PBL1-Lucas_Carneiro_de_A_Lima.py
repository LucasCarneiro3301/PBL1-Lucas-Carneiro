import string
import os
import platform

keywords = [
    'variables', 'var',
    'methods',
    'constants', 'const'
    'class', 
    'return', 
    'empty', 
    'main',
    'if',
    'then',
    'else',
    'while',
    'for',
    'read',
    'write',
    'integer', 'int',
    'float',
    'boolean', 'bool',
    'string',
    'true',
    'false',
    'extends'
]

identifiers = []

letters = list(string.ascii_lowercase) + list(string.ascii_uppercase)
digits = list(string.digits)
operators = ['+','-','*','/','=','!','>','<','&','|','.']
delimeters = [';',',','(',')','{','}','[',']']
alphanumeric = letters+digits+['_']
symbols = [chr(i) for i in range(32, 127) if i not in [34, 39]]

SIGMA = [chr(i) for i in range(32, 127)]
Q0 = ['q0'] # estado inicial
H = ['q1','q2','q3','q4','q5','q6','q7','q8','q9'] # estados intermediários
F = ['qid','qnum','qop1','qop2','qch','qstr','qdel','qulc', 'qbc','ech1','ech2', 'estr1', 'estr2', 'ebc', 'eop', 'elx'] # potenciais estados finais

def conditions(ch1, ch2, ch3,crstate, isLastElmnt):
    if(ch1 == ' ' and crstate in Q0+F): return 'q0'
    elif((crstate == 'q9') and (isLastElmnt)): return 'ebc'
    elif((crstate == 'q8') and (isLastElmnt) and (ch1 == '*')): return 'ebc'
    elif((ch1 == '"') and (ch2 == "'") and (crstate == 'q5')): return 'qaux1'
    elif((ch1 == "'") and (crstate == 'q6')): return 'qaux2'
    elif(crstate == 'qaux1'): return 'ech2'
    elif((crstate == 'qaux2') and (ch1 == '"')): return 'estr2'
    elif((crstate == 'qaux2') and (isLastElmnt)): return 'estr1'
    elif((isLastElmnt) and ch1=="'" and crstate in Q0+F): return 'ech1'
    elif((isLastElmnt) and ch1=='"' and crstate in Q0+F): return 'estr1'
    elif(((isLastElmnt) and (ch1 != '"')) and crstate == 'q6'): return 'estr1'
    elif((isLastElmnt) and (crstate == 'q7')): return 'qulc'
    elif((((ch1 in alphanumeric) and (ch2 in alphanumeric) and (crstate == 'q1')) or (ch1 in letters) and (ch2 in alphanumeric)) and crstate in Q0+F+['q1']): return 'q1'
    elif((((ch1 in digits) and (ch2 in digits)) or ((ch1 in digits) and (ch2 == '.') and (ch3 in digits)) or ((ch1 == '-') and (ch2 in digits) and (crstate == 'q0'))) and crstate in Q0+F+['q2']): return 'q2'
    elif((((ch1 in digits) and (ch2 in digits) and (crstate == 'q3')) or ((ch1 == '.') and (ch2 in digits))) and crstate in ['q2','q3']): return 'q3'
    elif((((ch1 in ['<','>','=']) and (ch2 == '=')) or ((ch1 == '-') and (ch2 == '-'))  or ((ch1 == '+') and (ch2 == '+')) or ((ch1 == '&') and (ch2 == '&')) or ((ch1 == '|') and (ch2 == '|'))) and crstate in Q0+F): return 'q4'
    elif((((ch1 in symbols) and (ch2 == "'") and (crstate == 'q5')) or ((ch1 == "'") and (crstate != 'q5'))) and crstate in Q0+F+['q5']): return 'q5'
    elif((((ch1 == '"') and (crstate != 'q6')) or ((ch1 in symbols) and (crstate == 'q6'))) and crstate in Q0+F+['q6']): return 'q6'
    elif((ch1 == ch2 == '/') and crstate in Q0+F+['q7']): return 'q7'
    elif((((ch1 == '*') and (ch2 == '/') and (crstate == 'q9')) or ((ch1 == '/') and (ch2 == '*') and (crstate != 'q9'))) and crstate in Q0+F+['q9']): return 'q8'
    elif((((ch1 == '*') and (crstate == 'q8')) or ((ch1 != '*') and (ch2 != '/') and (crstate == 'q9'))) and crstate in ['q8','q9']): return 'q9'
    elif(ch1 in delimeters and crstate in Q0+F): return 'qdel'
    elif((((ch1 in alphanumeric) and (ch2 not in alphanumeric) and (crstate == 'q1')) or (ch1 in letters) and (ch2 not in alphanumeric)) and crstate in Q0+F+['q1']): return 'qid'
    elif((ch1 == '"') and (crstate == 'q6')): return 'qstr'
    elif(((ch1 == "'") and (crstate == 'q5'))): return 'qch'
    elif((((ch1 in digits) and (ch2 not in digits) and (crstate == 'q3')) or ((ch1 in digits) and (ch2 not in digits+['.'])) or ((ch1 in digits) and (ch2 == '.') and (ch3 not in digits))) and crstate in Q0+F+['q2','q3']): return 'qnum'
    elif((((ch1 in ['<','>','=']) and (ch2 != '=')) or ((ch1 == '-') and (ch2 != '-'))  or ((ch1 == '+') and (ch2 != '+')) or ((ch1 in ['.','*'])) or ((ch1 == '/') and (ch2 not in ['*','/']))) and crstate in Q0+F): return 'qop1'
    elif((ch1 in ['=','-','+','&','|']) and (crstate == 'q4')): return 'qop2'
    elif((ch1 == '/') and (crstate == 'q8')): return 'qbc'
    elif((ch1 in symbols+['"']) and (ch2 != "'") and (crstate == 'q5')): return 'ech1'
    elif((((ch1 == '&') and (ch2 != '&')) or ((ch1 == '|') and (ch2 != "|"))) and crstate in Q0+F): return 'eop'
    elif((ch1 in symbols and ch1 not in letters+digits+delimeters+operators) and crstate in Q0+F): return 'elx'
    else: return crstate


class Automato:
    def __init__(self):
        self.currentState = 'q0'
    def transitions(self, ch1, ch2, ch3, isLastElmnt):
        self.currentState = conditions(ch1,ch2,ch3,self.currentState,isLastElmnt)

def verify(text):
    tokens = []
    errors = []
    sequence = ''
    length = len(text)
    count = 0
    automato = Automato()
    for ch1, ch2, ch3 in zip(text, text[1:] + ' ', text[2:] + '  '):
        if(ch1 in SIGMA):
            count=count+1
            automato.transitions(ch1, ch2, ch3,count==length)
            if(ch1 != ' ' or automato.currentState in ['q6','q5','q7','q8','q9']): sequence = sequence + ch1
            if(automato.currentState == 'qid'): 
                if(sequence in keywords): tokens.append({'type':'Keywords','value':sequence}) 
                else: 
                    tokens.append({'type':'Identifiers','value':sequence})
                    identifiers.append(sequence)
            elif(automato.currentState == 'qnum'):
                tokens.append({'type':'Numbers','value':sequence})
            elif(automato.currentState in ['qop1','qop2']):
                tokens.append({'type':'Operators','value':sequence})
            elif(automato.currentState in ['qch']):
                tokens.append({'type':'Character','value':sequence})
            elif(automato.currentState in ['qstr']):
                tokens.append({'type':'String','value':sequence})
            elif(automato.currentState in ['qdel']):
                tokens.append({'type':'Delimiters','value':sequence})
            elif(automato.currentState in ['qulc', 'qbc']):
                tokens.append({'type':'Comments','value':sequence})
            elif(automato.currentState in ['ech1']):
                errors.append({'Position':count,'Value':"A expressão \""+sequence+"\" não foi encerrada corretamente devido a ausência da segunda aspas simples (')",'Solution':"Insira a aspas simples (') na posição especificada"})
            elif(automato.currentState in ['ech2']):
                errors.append({'Position':count,'Value':'Não é permitido inserir aspas duplas (") em um token do tipo Character','Solution':"Remova as aspas duplas (\") do caractere"})
            elif(automato.currentState in ['estr1']):
                errors.append({'Position':count,'Value':"A expressão \""+sequence+"\" não foi encerrada corretamente devido a ausência da segunda aspas duplas (\")",'Solution':'Insira as aspas duplas (\") na posição especificada'})
            elif(automato.currentState in ['estr2']):
                errors.append({'Position':count,'Value':"Não é permitido inserir aspas simples (') em um token do tipo String",'Solution':"Remova todas as aspas simples (') da string"})
            elif(automato.currentState in ['ebc']):
                errors.append({'Position':count,'Value':"A expressão \""+sequence+"\" não foi encerrada corretamente devido a ausência de (*/)",'Solution':'Insira (*/) ao final do comentário em bloco na posição especificada'})
            elif(automato.currentState in ['eop']):
                errors.append({'Position':count,'Value':"O operador \""+sequence+"\" é inválido",'Solution':'Duplique o operador'})
            elif(automato.currentState in ['elx']):
                errors.append({'Position':count,'Value':"O elemento \""+sequence+"\" não possui um token correspondente",'Solution':'Verifique se o elemento faz parte de um caractere ou string.'})
            if(automato.currentState in F): sequence = ''
        else:
            errors.append({'Position':count,'Value':"O elemento '"+ch1+"' não é reconhecido",'Solution':'Remova o elemento inválido na posição especificada.'})
            break

    return [tokens, errors]
    

def clear_screen():
    if platform.system() == "Windows": os.system("cls")
    else: os.system("clear")

def main():
    results = ""
    errors = ""

    while True:
        clear_screen()

        # Frame 1
        print("#------------------------ ENTRADA ------------------------#")
        user_input = input("Digite algo: ")

        [tokens, errors] = verify(user_input)

        clear_screen()
        print("#------------------------ ENTRADA ------------------------#")
        print(user_input)  # Mostra o último input do usuário
        
        print("\n#------------------------ TOKENS -------------------------#")
        for i, token in enumerate(tokens):
            print(f"({i+1}) - <{token['type']}, {token['value']}>")

        print("\n#------------------------- ERROS -------------------------#")
        if(len(errors) == 0):
            print('Sucesso!!! O analisador léxico não identificou nenhum erro!')
        else:
            for i, error in enumerate(errors):
                print(f"ERRO ({i+1}): \n\t-POSIÇÃO: {error['Position']} \n\t-VALOR: {error['Value']} \n\t-SOLUÇÃO: {error['Solution']}")

        # Mantém o frame de entrada ativo para novas entradas
        input("\n\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
