import string
from itertools import *

# lista z dostępnymi nazwami zmiennych
var = string.ascii_lowercase
var += 'T' + 'F'

# funkcja sprawdzająca czy wyrażenie jest poprawne
def check(expr):
    operators = ('&', '|', '>', '^', '/') # krotka z dostępnymi operatorami
    counter = 0 # zmienna odpowiedzalna za zliczanie nawiasów, zwiększa się gdy nawias otwierający, zmniejsza się przy zamykającym
    status = True # gdy True oczekiwany jest nawias otwierający, zmienna lub negacja

    for ch in expr: # główna pętla funkcji odpowiedziala za zwiększanie/zmiejszania counter'a oraz zmiany statusu
        if status:
            if ch == '(':
                counter += 1
            elif ch in var:
                status = False
            elif ch == "~":
                pass
            else:
                return False
        else:
            if ch == ')':
                counter -= 1
            elif ch in operators:
                status = True
            else:
                return False
        if counter < 0: # więcej nawiasów zamykających niż otwierających więc wyrażenie jest niepoprawne
            return False

    if counter == 0 and not status: # tyle samo nawiasów oraz status jest fałszywy więc wyrażenie jest prawidłowe
        return True
    
    return False

# funkcja odpowiedzialna za usuwanie niepotrzebnych nawiasów
def bracket(w):
    if not check(w): return ""
    while w[0] == '(' and w[-1] == ')' and check(w[1:-1]):
        w = w[1:-1]
    return w

# funkcja zwracająca najbardziej prawą pozycję danego operatora
def bal(expr, ops):
    counter = 0

    for i in range(len(expr) - 1, -1, -1):
        if expr[i] == ')':
            counter += 1
        elif expr[i] == '(':
            counter -= 1
        elif counter == 0 and expr[i] in ops:
            return i

    return None


# funkcja zmieniającą podane wyrażenie z postaci algebricznej na postać ONP zachowując odpowienie priorytety
def onp(expr):
    expr = bracket(expr)
    if p := bal(expr, '>'): return onp(expr[:p]) + onp(expr[p + 1:]) + expr[p]
    if p := bal(expr, '&|/'): return onp(expr[:p]) + onp(expr[p + 1:]) + expr[p]
    if p := bal(expr, '^'): return onp(expr[:p]) + onp(expr[p + 1:]) + expr[p]
    p = bal(expr, '~')
    if p or (len(expr) > 0 and expr[0] == '~'): return onp(expr[:p]) + onp(expr[p + 1:]) + expr[p]
    return expr


# funkcja mapująca zmienne w wyrażeniu ONP na wartości z wektora 
def map(expr, vec):
    t = {sorted(list(set(expr).intersection(set(var))))[i]: vec[i] for i in range(len(vec))}
    for k in t:
        if k == 'T':
            expr = expr.replace(k, "1")
        elif k == 'F':
            expr = expr.replace(k, "0")
        else:
            expr = expr.replace(k, t[k])
    return expr


# funkcja obliczjąca wartość wyrażenia logicznego
def value(expr):
    st = []
    for ch in expr:
        if ch in '01':
            st.append(int(ch))
        elif ch == "~":
            p = st.pop()
            st.append(1 - p) 
        elif ch == '|':
            q = st.pop()
            p = st.pop()
            st.append(p or q)
        elif ch == '&':
            q = st.pop()
            p = st.pop()
            st.append(p and q)
        elif ch == '>':
            q = st.pop()
            p = st.pop()
            st.append((p and q) or (1 - p))
        elif ch == '^':
            q = st.pop()
            p = st.pop()
            st.append((p and 1 - q) or (1 - p and q))
        elif ch == '/':
            q = st.pop()
            p = st.pop()
            st.append(1 - (p and q))
        else:
            return None
    return st.pop()


# funkcja generująca wszystkie ciągi zero-jedynkowe długości n
def gen(n):
    res = []
    for i in range(2**n):
        res.append(f'{"".join(["0" for _ in range(n - len(bin(i)[2:]))])}{bin(i)[2:]}')
    return res


# funkcja zwracająca wszystkie wektory dla której wartość wyrażenia logicznego jest prawdziwa
def transform_to_vectors(expr):
    n = len(set(expr).intersection(set(var)))
    res = []
    for vec in gen(n):
        to_check = value(map(onp(expr), vec))
        if to_check:
            res.append(vec)

    return set(res)

# funkcja łącząca dwa wektory w jeden gdy różnią się na dokładnie jednej pozycji. W różniącej się pozycji wstawiana jest "-"
def lacz(vec1,vec2):
    counter = 0
    result = ""

    for i in range(len(vec1)):
        if vec1[i]== vec2[i]: 
            result += vec1[i]
        else: 
            result += '-'
            counter += 1 

    if counter == 1:
        return result
    return None


# funkcja redukująca zbiór według zasad:
# 1) dla każdego wektora jeżeli łączy się z innym do zbioru wynikowego przechodzi wynik łączenia wektorów
# 2) każdy wektora, który nie łączy się z innym, przechodzi do zbioru wynikowego
def redukuj(vectors):
    result = set([])
    b1 = False
    for v1 in vectors:
        b2 = False
        for v2 in vectors:
            n = lacz(v1,v2)
            if n:
                result.add(n)
                b1 = b2 = True
        if not b2:
            result.add(v1)
    if b1: 
        return redukuj(result)
    else: 
        return result


# funkcja zwracająca użyte w wyrażeniu zmienne 
def used_var(e):
    res = []
    for ch in e:
        if ch in string.ascii_lowercase and ch not in res:
            res.append(ch)

    return res


# funkcja zmieniająca zbiór wektorów w postać DNF
def wyr(s, variables):
    res = ""
    for e in s:
        res2 = ""
        for i in range(len(e)):
            if e[i]=='-':
                continue
            if e[i]=='0': 
                res2 += "~"
            res2 += variables[i]+'&'
        res += "("+res2[:-1]+")|"
    return res[:-1]


# funkcja sprawdzająca czy wektor pasuje do wzorca
def match(x,w):
    for i in range(len(x)):
        if w[i] == '-': continue
        if w[i] != x[i]: return False
    return True


# funkcja wybierająca z zbioru wzorców minimalny podzbiór, tak żeby każdy wektor pasował do wybranego podzbioru
def minp(vectors, patterns):
    for pattern in range(1,len(patterns)):
        for c in combinations(patterns, pattern):
            nowy = set()
            for el in vectors:
                for wz in c: 
                    if match(el,wz):
                        nowy.add(el)
            if len(nowy)==len(vectors):
                return c
    return patterns


# funkcja usuwająca niepotrzebne negacje np. "~~a" -> "a"
def remove_negations(e):
    flag = False
    to_change = []
    for indx, ch in enumerate(e):
        if ch == '~' and not flag:
            flag = True
        elif ch != '~' and flag:
            flag = False
        elif ch == '~' and flag:
            to_change.append(indx-1)
            to_change.append(indx)
            flag = False
    
    for indx in to_change:
        e = e[:indx] + " " + e[indx + 1:]
    return e.replace(" ", "")

# funkcja usuwająca niepotrzebne nawiasy pomiędzy samymi zmiennymi np. "(a)" -> a
def bracket2(e):
    to_change = []
    for i in range(len(e)):
        if e[i] == '(' and e[i+1] in var and e[i+2] == ')':
            to_change.append(i)
            to_change.append(i+2)
        elif e[i] == '(' and e[i+1] == '~' and e[i+2] in var and e[i+3] == ')':
            to_change.append(i)
            to_change.append(i+3)

    for indx in to_change:
        e = e[:indx] + " " + e[indx + 1:]
    return e.replace(" ", "")


# funkcja tworząca wyrażenie logiczne z postaci wektorów
def create_expression(vectors, variables):
    vectors = sorted(vectors)
    
    if vectors == ['-1','0-']: # wzorzec "a>b"
        return f"{variables[0]}>{variables[1]}"

    if vectors == ['01', '10']: # wzorzec "a^b"
        return f"{variables[0]}^{variables[1]}"

    if vectors == ['-0','0-']: # wzorzec "a/b"
        return f"{variables[0]}/{variables[1]}"
    
    if vectors == ['--1', '10-']: # wzorzec "a>b>c"
        return f"{variables[0]}>{variables[1]}>{variables[2]}"
    
    if vectors == ['001', '010', '100', '111']: # wzorzec "a^b^c"
        return f"{variables[0]}^{variables[1]}^{variables[2]}"
    
    if vectors == ['--0', '11-']: # wzorzec "a/b/c"
        return f"{variables[0]}/{variables[1]}/{variables[2]}"
    
    if vectors == ['---1', '-10-', '0-0-']: # wzorzec "a>b>c>d"
        return f"{variables[0]}>{variables[1]}>{variables[2]}>{variables[3]}"
    
    if vectors == ['0001', '0010', '0100', '0111', '1000', '1011', '1101', '1110']: # wzorzec "a^b^c^d"
        return f"{variables[0]}^{variables[1]}^{variables[2]}^{variables[3]}"
    
    if vectors == ['---0', '-01-', '0-1-']: # wzorzec "a/b/c/d"
        return f"{variables[0]}/{variables[1]}/{variables[2]}/{variables[3]}"
    
    if vectors == ['----1', '--10-', '10-0-']: # wzorzec "a>b>c>d>e"
        return f"{variables[0]}>{variables[1]}>{variables[2]}>{variables[3]}>{variables[4]}"
    
    if vectors == ['00001', '00010', '00100', '00111', '01000', '01011', '01101', '01110', '10000', '10011', '10101', '10110', '11001', '11010', '11100', '11111']: # wzorzec "a^b^c^d^e"
        return f"{variables[0]}^{variables[1]}^{variables[2]}^{variables[3]}^{variables[4]}"
    
    if vectors == ['----0', '--01-', '11-1-']: # wzorzec "a/b/c/d/e"
        return f"{variables[0]}/{variables[1]}/{variables[2]}/{variables[3]}/{variables[4]}"

    return wyr(vectors, variables) # jeżeli nie dopasowano do wzorca zwraca jest postać DNF


# główna funkcja, łącząca inne
def solution(e):
    e = e.replace(" ", "") # usuwanie spacji
    
    if not check(e): # jeżeli wyrażenie nie jest poprawne zwracany jest "ERROR"
        return "ERROR"
    
    e = bracket(e) # usuwanie niepotrzebnych nawaisów
    e = remove_negations(e) # usuwanie niepotrzebnych negacji
    s = transform_to_vectors(e) # tworzenie zbioru wektorów, dla którch wyrażenie jest prawdziwe 
    s1 = redukuj(s) # redukowanie zbioru wektorów do minimalnej postaci
    s2 = minp(s, s1) # wybieranie minimalnego podzbioru wzorców pasujących do zbioru wektorów
    
    # przypadek zwracania "T" lub "F"
    if len(s2) == 1:
        for ex in s2:
            for ch in ex:
                if ch != '-':
                    break
            else:
                return 'T'
    elif not s2:
        return 'F'
    
    variables = used_var(e) # tworzenie listy używanych zmiennych

    mini = bracket2(bracket(create_expression(s2, variables))) # minimalizacja wyrażenia logicznego na tyle ile potrafi program

    # jeżeli nie udało się zredukować wyrażenie zwracana jest pierwotna postać
    if len(mini) >= len(e):
        return e
    
    return mini

if __name__ == "__main__":
    print(solution(input()))