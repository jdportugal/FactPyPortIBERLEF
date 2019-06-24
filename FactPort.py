import re
from FullPipeline import *
import sys

def rule_sorte(valores_e_regras):
    valores = []
    regras = []
    rank = []
    pos = []
    return_pos = []
    for i in range(len(valores_e_regras)):
        ##print(valores_e_regras[i])
        coisa = valores_e_regras[i].split("§")
        valores.append(coisa[0])
        pos.append(coisa[1])
        regras.append(coisa[2])
    ##print(valores,regras)
    #ordem_regras = [i[0] for i in sorted(enumerate(valores), key=lambda x:x[1],reverse=True)]
    ordem_regras = [i[0] for i in sorted(enumerate(regras), key=lambda x:len(x[1]),reverse=True)]
    ##print(ordem_regras)
    regras_ordenadas = []
    for i in range(len(ordem_regras)):
        regras_ordenadas.append(regras[ordem_regras[i]])
        rank.append(valores[ordem_regras[i]])
        return_pos.append(pos[ordem_regras[i]])
    return regras_ordenadas,rank,return_pos

def verify_and_save_rule(rule_file,rule,posicoes):
    exists = 0
    regras = []
    pos = []
    rules,rank,pos = load_rules(rule_file)
    for r in rules:
        regras.append(r)
        if(r.strip("\n")==rule):
            exists = 1
    if(exists == 0):
        #Regra principal
        regras.append(rule)
        rank.append("1")
        posicoes_string = ""
        for ele in posicoes:
            posicoes_string+=str(ele)
        pos.append(posicoes_string)

         #Regra alternativa
        if("0" in posicoes_string):
            nova_regra_tags = ""
            num_zeros = 0
            regra_dividida = rule.split(" ")
            for index,i in enumerate(posicoes):
                if(i!=0):
                    nova_regra_tags+=regra_dividida[index] + " "
                    num_zeros+=1
            nova_regra_tags = nova_regra_tags[:-1]
            indices = np.ones(num_zeros,dtype=int)
            posicoes_string = ""
            for ele in indices:
                posicoes_string+=str(ele)
            indices = posicoes_string
            if(not nova_regra_tags in regras):
                regras.append(nova_regra_tags)
                rank.append("1")
                pos.append(indices)

        open(rule_file,'w').close()
        with open(rule_file,"a") as f:
            for index,r in enumerate(regras):
                if(len(r)>0):
                    f.write(rank[index]+"§"+str(pos[index])+"§"+str(r)+"\n")
        return 1
    return 0

def encontra_entidade(entidade,tokens,texto_tem_traco=1):
    if(texto_tem_traco==0):
        entidade1_dividida = entidade.split("_")
        if(len(entidade1_dividida)==1):
            entidade1_dividida = entidade1_dividida[0].split(" ")
        index = 0
        meio = 0
        for j in range(len(entidade1_dividida)):
                for i in range(len(tokens)):
                        if(tokens[i]==entidade1_dividida[j]):
                            if(j==1):
                                meio=1
                                if(j<len(entidade1_dividida)):
                                    j+=1
                            if(j==len(entidade1_dividida)-1):
                                index = i
                                break
                            else:
                                if(j<len(entidade1_dividida)):
                                    j+=1
                        else:
                            if(meio==1):
                                meio = 0
        return index-1
    else:
        for index,tok in enumerate(tokens):
            if(tok==entidade):
                return index
    return -1

def processa_regra_v2(frase,entidade1,entidade2,relacao):
    #print("########"+str(relacao)+"######")
    tokens,tags = custom_pipe(frase)
    inicio = encontra_entidade(entidade1,tokens)
    fim = encontra_entidade(entidade2,tokens)
    tokens_rel,tags_rel = custom_pipe(relacao)
    tokens_rel = tokens_rel[:-1]
    tags_rel = tags_rel[:-1]
    relacao_string = ""
    tam_rel = fim-inicio-1
    for tok in tokens_rel:
        tam_rel+=1
        relacao_string+=tok.lower() + " "
    relacao_string=relacao_string[:-1]
    '''
    if(tam_rel>1):
        inicio_relacao = encontra_entidade(relacao_string,tokens,0)-(tam_rel-2)
    else:
        inicio_relacao = encontra_entidade(relacao_string,tokens,1)
    '''
    full_tags_found = []
    tags_relacao_sem_exclusoes = tags[inicio+1:fim]
    tokens_relacao_sem_exclusoes = tokens[inicio+1:fim]
    #print("tokens_relacao_sem_exclusoes",tokens_relacao_sem_exclusoes)
    #print("TAG",tags_relacao_sem_exclusoes)
    indices = np.zeros(len(tokens_relacao_sem_exclusoes),dtype=int)
    for index,i in enumerate(tokens_relacao_sem_exclusoes):
        if(i in tokens_rel):
            indices[index] = 1

    regra = ""
    for i in range(len(tags_relacao_sem_exclusoes)):
        regra += tags_relacao_sem_exclusoes[i].split("-")[0].lower() + " "
    regra = regra[:-1]
    #print("-------"+str(regra)+"----------")
    return regra,indices

def processa_regra(frase,entidade1,entidade2,relacao):
    tokens,tags = custom_pipe(frase)
    inicio = encontra_entidade(entidade1,tokens)
    fim = encontra_entidade(entidade2,tokens)
    tokens_rel,tags_rel = custom_pipe(relacao)
    tokens_rel = tokens_rel[:-1]
    tags_rel = tags_rel[:-1]
    relacao_string = ""
    tam_rel = 0
    for tok in tokens_rel:
        tam_rel+=1
        relacao_string+=tok.lower() + " "
    relacao_string=relacao_string[:-1]
    if(tam_rel>1):
        inicio_relacao = encontra_entidade(relacao_string,tokens,0)-(tam_rel-2)
    else:
        inicio_relacao = encontra_entidade(relacao_string,tokens,1)
    fim_relacao = inicio_relacao + tam_rel
    regra = ""
    for i in range(inicio_relacao,fim_relacao):
        regra += tags[i].split("-")[0].lower() + " "
    regra = regra[:-1]
    return regra

def manual_train2(file_name,rules_file):
    #ler input
    frase = []
    entidade1 = []
    entidade2 = []
    relacao = []
    with open(file_name,"r") as f:
        for index,line in enumerate(f):
            #print("<<"+str(index)+">>")
            coisas = line.split("\t")
            #print(str(coisas))
            frase_currente = []
            frase_currente.append(coisas[2].strip("\n"))
            frase.append(frase_currente)
            #frase_currente.append(coisas[2])
            #print(coisas[3])
            entidade1.append(coisas[3])

            frase_currente = []
            frase_currente.append(coisas[5].strip("\n"))
            relacao.append(frase_currente)

            #print(coisas[6])
            entidade2.append(coisas[6])
    for i in range(len(frase)):
        regra,posicoes = processa_regra_v2(frase[i],entidade1[i],entidade2[i],relacao[i])
        verify_and_save_rule(rules_file,regra,posicoes)

def manual_train(file_name,rules_file):
    #ler input
    frase = []
    entidade1 = []
    entidade2 = []
    relacao = []
    with open(file_name,"r") as f:
        for line in f:
            if(line.split(" ")[0]=="SENTENCE"):
                frase_currente = []
                frase_currente.append(line.split(":")[1].strip("\n"))
                frase.append(frase_currente)
            elif(line.split(" ")[0]=="ENTITY1"):
                entidade_currente = line.split(":")[1].strip("\n")
                entidade1.append(entidade_currente)
            elif(line.split(" ")[0]=="ENTITY2"):
                entidade_currente = line.split(":")[1].strip("\n")
                entidade2.append(entidade_currente)
            elif(line.split(" ")[0]=="RELTYPE"):
                relacao_currente =[]
                relacao_currente.append(line.split(":")[1].strip("\n"))
                relacao.append(relacao_currente)

    for i in range(len(frase)):
        regra,posicoes = processa_regra_v2(frase[i],entidade1[i],entidade2[i],relacao[i])
        verify_and_save_rule(rules_file,regra,posicoes)


def load_rules(rules_file):
    unordered_rules = []
    with open(rules_file,"r") as f:
        for line in f:
            unordered_rules.append(line[:-1])
    rules,rank,pos = rule_sorte(unordered_rules)
    return rules,rank,pos

def sort_rules(unordered_rules):
    rules,rank,pos = rule_sorte(unordered_rules)
    return rules,rank,pos

def update_rule(rule_file,r,entidade1,entidade2,frase):
    #print("funcao de alterar")
    #print(r)
    regras=[]
    ranking = []
    rule = ""
    for word in r:
        rule+=word+" "
    rule = rule[:-1]
    rules,rank,pos = load_rules(rule_file)
    rank_string = []
    vall = 0
    #processa_regra_v2(frase,entidade1,entidade2,r)
    ##print("this_rule",r)
    for index,rul in enumerate(rules):
        #print("percorrer regras",rul)
        if(r==rul):
            vall=1
            print("Alterada")
            rank[index] = int(rank[index])+1
        rank_string.append(str(rank[index])+"§"+pos[index]+"§"+rul)
    regras,rank,pos = sort_rules(rank_string)
    open(rule_file,'w').close()
    with open(rule_file,"a") as f:
        for index,rul in enumerate(regras):
            if(len(rul)>0):
                f.write(rank[index]+"§"+pos[index]+"§"+str(rul)+"\n")
            ##print(r)

def verifica_correta_vteste(rule_file,regra,entidade1,entidade2,frase):
    correta = input("A relação identificada está correta? (s ou n)\n")
    if(correta=="s"):
        #print(type(regra))
        regra_string = ""
        for elem in regra:
            regra_string+=elem+" "
        regra_string = regra_string[:-1]
        update_rule(rule_file,regra_string,entidade1,entidade2,frase)
    if(correta=="n"):
        rel = input("Qual a relação correta?(copiar e colar as palavras correspondentes)\n")
        relacao = [rel]
        regra,pos = processa_regra_v2(frase,entidade1,entidade2,relacao)
        update_rule(rule_file,regra,entidade1,entidade2,frase)
        #verify_and_save_rule(rule_file,regra,pos)

def verifica_correta(rule_file,regra,entidade1,entidade2,frase):
    correta = input("A relação identificada está correta? (s ou n)\n")
    if(correta=="s"):
        update_rule(rule_file,regra,entidade1,entidade2,frase)
    if(correta=="n"):
        rel = input("Qual a relação correta?(copiar e colar as palavras correspondentes)\n")
        relacao = [rel]
        regra,pos = processa_regra_v2(frase,entidade1,entidade2,relacao)
        rule_list = []
        for ele in regra.split(" "):
            rule_list.append(ele)
        res = verify_and_save_rule(rule_file,regra,pos)
        if(res==0):
            update_rule(rule_file,regra,entidade1,entidade2,frase)


def make_test2(file_name,rule_file,debug):
    print("SENTENCE_ID"+"\t"+"RELATION_ID SENTENCE"+"\t"+"ARGUMENT_2"+"\t"+"ARGUMENT_1_CATEGORY"+"\t"+"RELATION"+"\t"+"ARGUMENT_2"+"\t"+"ARGUMENT_2_CATEGORY")
    frase_id_1 = []
    frase_id_2 = []
    frase = []
    entidade1 = []
    entidade2 = []
    #relacao = []
    tipo_ent1 = []
    tipo_ent2 = []
    with open(file_name,"r") as f:
        for index,line in enumerate(f):
            if(index>0):
                coisas = line.split("\t")
                #print(str(coisas))
                frase_id_1.append(coisas[0])
                frase_id_2.append(coisas[1])
                frase_currente = []
                frase_currente.append(coisas[2].strip("\n"))
                frase.append(frase_currente)
                #frase_currente.append(coisas[2])
                #print(coisas[3])
                entidade1.append(coisas[3])
                tipo_ent1.append(coisas[4])
                #frase_currente = []
                #frase_currente.append(coisas[5].strip("\n"))
                #relacao.append(frase_currente)
                #print(coisas[6])
                entidade2.append(coisas[5])
                tipo_ent2.append(coisas[6])
    certas = 0
    erradas = 0
    for i in range(len(frase)):
        rules,rank,pos = load_rules(rule_file)
        resultado,tags_resultado,pos_res = test_rules(frase[i],entidade1[i],entidade2[i],rules)
        if(resultado!=[]):
            final = ""
            ant = ""
            for j in range(len(resultado)):
                if(pos[pos_res][j]=="1"):
                    if(resultado[j]!=ant):
                        final += resultado[j] + " "
                        ant = resultado[j] 
            final = final[:-1]
            print(str(frase_id_1[i]) + "\t" + str(frase_id_2[i])+ "\t" + str(frase[i][0])+"\t"+str(entidade1[i])+"\t"+str(tipo_ent1[i])+"\t"+str(final)+"\t"+str(entidade2[i])+"\t"+str(tipo_ent2[i]))
            #print(str(final + "|" + str(relacao[i][0])))
            #if(str(final) == str(relacao[i][0])):
            #    certas+=1
            #else:
            #    erradas+=1
            if(debug==True):
                verifica_correta(rule_file,tags_resultado,entidade1[i],entidade2[i],frase[i])
        else:
            print("Não foi encontrada relacao")
            if(debug==True):
                verifica_correta(rule_file,tags_resultado,entidade1[i],entidade2[i],frase[i])

def make_test(file_name,rule_file,debug):
    frase = []
    entidade1 = []
    entidade2 = []
    with open(file_name,"r") as f:
        for line in f:
            if(line.split(" ")[0]=="SENTENCE"):
                frase_currente = []
                frase_currente.append(line.split(":")[1].strip("\n"))
                frase.append(frase_currente)
            elif(line.split(" ")[0]=="ENTITY1"):
                entidade_currente = line.split(":")[1].strip("\n")
                entidade1.append(entidade_currente)
            elif(line.split(" ")[0]=="ENTITY2"):
                entidade_currente = line.split(":")[1].strip("\n")
                entidade2.append(entidade_currente)
    for i in range(len(frase)):
        rules,rank,pos = load_rules(rule_file)
        resultado,tags_resultado,pos_res = test_rules(frase[i],entidade1[i],entidade2[i],rules)
        if(resultado!=[]):
            final = ""
            for j in range(len(resultado)):
                if(pos[pos_res][j]=="1"):
                    final += resultado[j] + " "
            final = final[:-1]
            print(entidade1[i]+" " + str(final) + " "+entidade2[i]+"\n")
            if(debug==True):
                verifica_correta(rule_file,tags_resultado,entidade1[i],entidade2[i],frase[i])
        else:
            print("Não foi encontrada relacao")
            if(debug==True):
                verifica_correta(rule_file,tags_resultado,entidade1[i],entidade2[i],frase[i])

def test_rules(frase,entidade1,entidade2,rules):
    tokens,tags = custom_pipe(frase)
    inicio = encontra_entidade(entidade1,tokens)+1
    fim = encontra_entidade(entidade2,tokens)
    relacao_string = " "
    for i in range(len(tags)):
        tags[i] = tags[i].split("-")[0]

    for index,elem in enumerate(rules):
        found = 0
        middle = 0
        inicio_frase = 0
        fim_frase = 0
        rule_part = elem.lower()
        divided_rules = rule_part.split(" ")
        for index_tag in range(inicio,fim):
            for index_rule in range(len(divided_rules)):
                if(tags[index_tag].lower()==divided_rules[index_rule].lower()):
                    found+=1
                    if(index_rule==0):
                        middle=1
                        inicio_frase=index_tag
                    if(found==len(divided_rules) and middle==1):
                        #print(tokens[inicio_frase:index_tag+1],tags[inicio_frase:index_tag+1])
                        #print(len(divided_rules))
                        return tokens[inicio_frase:index_tag+1],tags[inicio_frase:index_tag+1],index
                    else:
                        if(index_tag+1<fim):
                            index_tag = index_tag + 1
                else:
                    middle=0
                    inicio_frase=0
                    fim_frase=0
                    found = 0
    return [],[],0

def outside_verbal_forms():
    rules = []
    beging_rule = re.compile(r"ent\s(\s|[^v])*")
    end_rule = re.compile(r"v\s(\s|[^v])*ent")
    rules.append(beging_rule)
    rules.append(end_rule)
    return rules

def rule_based_sistem(tokens,tags):
    '''
    Detect the verb form and return it
    In case of many return from the first to the last verb form
    '''
    tags_text = prep_data(tags)
    verb_rules = outside_verbal_forms()
    inicio = -1
    fim = -1
    for regra in verb_rules:
        result = re.search(regra,tags_text)
        if(inicio==-1):
            inicio = result.end()
        else:
            fim = result.start()+1
    tokens_inicio = tags_text[0:inicio-1].split(" ")
    tokens_fim = tags_text[fim+1:-1].split(" ")
    tokens_meio = tags_text[inicio:fim].split(" ")
    index_inicio = len(tokens_inicio)
    index_fim = len(tokens_meio)+index_inicio

def prep_data(tags):
    text =""
    for i in (tags):
        text+=i + " "
    return text


if __name__ == "__main__": 
    if(len(sys.argv)>1):
        make_test2(sys.argv[1],"rules3.txt",False)
    else:
        make_test2("testes.txt","rules3.txt",False)
