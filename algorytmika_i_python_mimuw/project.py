import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Model Hassella", layout="wide")
st.title("Interaktywny Model Populacyjny Hassella")

# --- FUNKCJE ---

def calculate_next_hassell(xt, l, b):
    '''
    Oblicza wartość x(t+1) na podstawie x(t) dla modelu Hassella.
    xt: populacja w roku t
    l: tempo wzrostu (lambda)
    b: typ konkurencji (beta)
    '''
    return l * xt * (1 + xt)**(-b)

@st.cache_data
def calculate_iterations(xt, l, b, iterations=1000, show_last=100):
    '''
    Oblicza trajektorię populacji przez określoną liczbę iteracji, ale zwraca tylko ostatnie N wartości.
    xt: początkowa populacja
    l: tempo wzrostu (lambda)
    b: typ konkurencji (beta)
    iterations: ile iteracji wykonać w sumie (domyślnie 1000)
    show_last: ile ostatnich wartości zwrócić (domyślnie 100)
    '''
    if iterations <= show_last:
        iterations = show_last + 500 
    x = xt
    for _ in range(iterations - show_last):
        x = l * x * (1 + x)**(-b)
    result = np.zeros(show_last)
    for i in range(show_last):
        x = l * x * (1 + x)**(-b)
        result[i] = x
    return result


def check_type(iters):
    '''
    Na podstawie liczby unikalnych wartości w trajektorii (po zaokrągleniu) określa typ zachowania:
    0: Stabilny punkt stały (1 unikalna wartość)
    1: Okres 2 (2 unikalne wartości)
    2: Okres 3 (3 unikalne wartości)
    3: Okres 4 (4 unikalne wartości)
    4: Okres 5-8 (5-8 unikalnych wartości)
    5: Okres 8-16 (9-16 unikalnych wartości)
    6: Chaos (więcej niż 16 unikalnych wartości)
    '''
    slownik_wystapien = {}
    for val in iters:
        rounded_val = round(val, 6)
        if rounded_val in slownik_wystapien:
            slownik_wystapien[rounded_val] += 1
        else:
            slownik_wystapien[rounded_val] = 1
    unikalne = len(slownik_wystapien)
    if unikalne == 1: return 0  
    elif unikalne == 2: return 1
    elif unikalne == 3: return 2
    elif unikalne == 4: return 3
    elif 5 <= unikalne <= 8: return 4
    elif 8 < unikalne <= 16: return 5
    else: return 6

def plot_trajectory(xt, l, b, iterations=1000, show_last=100):
    '''
    Rysuje trajektorię populacji w czasie dla podanych parametrów.
    xt: początkowa populacja
    l: tempo wzrostu (lambda)
    b: typ konkurencji (beta)
    iterations: ile iteracji wykonać w sumie (domyślnie 1000)
    show_last: ile ostatnich wartości pokazać na wykresie (domyślnie 100)
    '''
    fig_traj, ax_traj = plt.subplots(figsize=(10, 4))
    iters = calculate_iterations(xt, l, b, iterations=iterations, show_last=show_last)
    ax_traj.plot(iters, marker='o', markersize=4, linestyle='-', color='blue')
    ax_traj.set_title(f"Trajektoria (ostatnie {show_last} pokoleń) | λ = {l} | β = {b}")
    ax_traj.grid(True)
    st.pyplot(fig_traj) 

def plot_bifurcation_map(x_start, lambda_vals, beta_val, iterations = 1000, show_last=100):
    '''
    Rysuje mapę bifurkacji dla stałej wartości beta i zakresu lambda.
    Argumenty:
    x_start: początkowa wartość populacji
    lambda_vals: tablica wartości lambda do przetestowania
    beta_val: stała wartość beta
    iterations: ile iteracji wykonać dla każdego lambda (domyślnie 1000)
    show_last: ile ostatnich wartości pokazać na wykresie dla każdego lambda (domyślnie 100)
    '''
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.full(len(lambda_vals), x_start)
    for _ in range(iterations):
        x = calculate_next_hassell(x, lambda_vals, beta_val)
    X_plot, Y_plot = [], []
    for _ in range(show_last):
        x = calculate_next_hassell(x, lambda_vals, beta_val)
        X_plot.extend(lambda_vals)
        Y_plot.extend(x)
    ax.scatter(X_plot, Y_plot, s=0.5, color='blue')
    ax.set_xlabel("Lambda")
    ax.set_ylabel("Populacja (X)")
    ax.set_title(f"Mapa Bifurkacji dla Beta = {beta_val}")
    ax.grid(True)
    st.pyplot(fig)


def plot_return_map(l, b):
    '''
    Rysuje mapę powrotu (X(t) vs X(t+1)) dla stałych wartości lambda i beta.
    '''
    fig, ax = plt.subplots(figsize=(12, 4))
    x_t = np.linspace(0.01, 1.0, 1000)
    x_t1 = calculate_next_hassell(x_t, l, b)
    ax.scatter(x_t[:-1], x_t1[1:], s=10, color='blue')
    ax.set_xlabel("X(t)")
    ax.set_ylabel("X(t+1)")
    ax.set_title(f"Mapa powrotu dla λ = {l} | β = {b}")
    ax.grid(True)
    st.pyplot(fig)

def plot_cobweb(x_0, l, b, iterations=100):
    # 1. Obliczanie punktów trajektorii
    x_history = [x_0]
    x_current = x_0
    for _ in range(iterations):
        x_next = calculate_next_hassell(x_current, l, b)
        x_history.append(x_next)
        x_current = x_next
        
    # 2. Generowanie schodków pajęczyny
    # Ścieżka: (x0, 0) -> (x0, x1) -> (x1, x1) -> (x1, x2) -> ...
    px, py = [], []
    for i in range(len(x_history) - 1):
        # Pionowa linia z y=x do f(x)
        px.append(x_history[i])
        py.append(x_history[i] if i > 0 else 0)
        
        px.append(x_history[i])
        py.append(x_history[i+1])
        
        # Pozioma linia z f(x) do y=x
        px.append(x_history[i])
        py.append(x_history[i+1])
        
        px.append(x_history[i+1])
        py.append(x_history[i+1])

    # 3. Dynamiczne skalowanie osi (aby wykres był czytelny)
    max_x = max(x_history) * 1.2 if max(x_history) > 0 else 1.0
    x_vals = np.linspace(0, max_x, 500)
    y_vals = calculate_next_hassell(x_vals, l, b)
    
    # 4. Rysowanie wykresu
    fig, ax = plt.subplots(figsize=(12, 6)) # Kwadratowy wykres jest najlepszy
    
    # Rysowanie linii bazowych
    ax.plot(x_vals, y_vals, label='f(x) - Model Hassella', color='blue', linewidth=2)
    ax.plot(x_vals, x_vals, label='y = x', color='gray', linestyle='--')
    
    # Rysowanie pajęczyny
    ax.plot(px, py, color='red', linewidth=1, alpha=0.7, label='Pajęczyna (Odbicia)')
    
    # Punkt startowy
    ax.plot(x_0, 0, marker='o', color='green', markersize=6, label=f'Start X0={x_0}')
    
    # Przecięcia (Punkty stałe)
    ax.set_title(f"Diagram Pajęczynowy (λ = {l:.2f}, β = {b:.2f})")
    ax.set_xlabel("Populacja w roku t: x(t)")
    ax.set_ylabel("Populacja w roku t+1: x(t+1)")
    ax.legend()
    ax.grid(True)
    
    st.pyplot(fig)



@st.cache_data 
def generate_bifurcation_heatmap(x_0, res_lambda, res_beta, min_lambda = 0.1, max_lambda = 100, min_beta = 0.1, max_beta = 5):
    """Ta funkcja wyliczy się tylko raz i zapisze w pamięci, chyba że zmienisz parametry wejściowe."""
    lambda_vals = np.linspace(min_lambda, max_lambda, res_lambda)
    beta_vals = np.linspace(min_beta, max_beta, res_beta)
    
    Z = np.zeros((len(beta_vals), len(lambda_vals)))
    for i, b in enumerate(beta_vals):
        for j, l in enumerate(lambda_vals):
            iters = calculate_iterations(x_0, l, b)
            Z[i, j] = check_type(iters)
            
    return lambda_vals, beta_vals, Z












# --- INTERFEJS UŻYTKOWNIKA (UI) ---
st.sidebar.header("Parametry symulacji")
x0 = st.sidebar.slider("Początkowa populacja (X0)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)

# TRAJEKTORIA
st.markdown("### 1. Pojedyncza Trajektoria")
st.text("Dostosuj parametry Lambda i Beta, aby zobaczyć trajektorię populacji w czasie. Wyświetlane jest ostatnie N iteracji.")
col1_1, col1_2, col1_3 = st.columns(3)

with col1_1:
    l_val = st.slider("Parametr Lambda (λ) - Tempo wzrostu", 0.1, 300.0, 15.0, 0.1)
with col1_2:
    b_val = st.slider("Parametr Beta (β) - Typ konkurencji", 0.1, 20.0, 2.2, 0.1)
with col1_3:
    last_n = st.slider("Pokazywane iteracje (ostatnie)", 100, 1000, 100, 100)

# Rysowanie trajektorii w czasie rzeczywistym
plot_trajectory(x0, l_val, b_val, iterations=1000, show_last=last_n)






# MAPA POWROTU
st.markdown("---")
st.markdown("### 2. Mapa Powrotu")
plot_return_map(l_val, b_val)






# MAPA BIFURKACJI
st.markdown("### 2. Mapa Bifurkacji")

col2_1, col2_2 = st.columns(2)
with col2_1:
    beta_const = st.slider("Beta (β) dla mapy bifurkacji", 0.1, 20.0, 2.2, 0.1, key="bif_beta")
with col2_2:
    last_n_bif = st.slider("Pokazywane iteracje (ostatnie) dla mapy bifurkacji", 100, 1000, 100, 100, key="bif_last_n")

plot_bifurcation_map(
    x_start=x0,
    lambda_vals=np.linspace(0.1, 100, 150), 
    beta_val=beta_const, 
    show_last=last_n_bif
)





# COBWEB
st.markdown("---")
st.markdown("### 3. Diagram Pajęczynowy (Cobweb)")
plot_cobweb(x0, l_val, b_val, iterations=100)





# ANIMACJA
st.markdown("---")
st.markdown("### 2. Animacja przejścia w chaos")
st.write("Płynna zmiana parametru Lambda, aby zaobserwować moment utraty stabilności.")

col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
    l_start = st.number_input("Lambda startowa", min_value=0.1, value=1.0, step=1.0)
    l_end = st.number_input("Lambda końcowa", min_value=1.0, value=100.0, step=1.0)
with col_a2:
    anim_b = st.slider("Parametr Beta (β) dla animacji", 0.1, 20.0, 2.2, 0.1, key="anim_beta")
    anim_last_n = st.slider("Pokazywane iteracje (ostatnie)", 100, 1000, 100, 100, key="anim_last_n")
with col_a3:
    frames = st.slider("Liczba klatek (płynność)", 10, 150, 100)
    delay = st.slider("Opóźnienie klatki (s)", 0.01, 0.2, 0.03)

if st.button("▶ Odtwórz animację"):
    # Rezerwujemy puste miejsce na wykres i pasek postępu
    plot_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    # Generujemy tablicę wartości lambda od startu do końca
    l_values = np.linspace(l_start, l_end, frames)
    
    # Pre-kalkulacja maksymalnej wartości Y, żeby oś Y nie skakała podczas animacji
    # Zabezpiecza to przed irytującym miganiem skali wykresu
    max_y_global = 0.1
    
    for current_l in l_values:
        fig_anim, ax_anim = plt.subplots(figsize=(10, 4))
        iters_anim = calculate_iterations(x0, current_l, anim_b, show_last=anim_last_n)
        
        # Rysowanie klatki
        ax_anim.plot(iters_anim, marker='o', markersize=4, linestyle='-', color='crimson')
        ax_anim.set_title(f"Trajektoria dla λ = {current_l:.2f} | β = {anim_b}")
        
        # Skalowanie osi Y
        max_y_current = max(iters_anim)
        if max_y_current > max_y_global:
            max_y_global = max_y_current
        ax_anim.set_ylim(0, max_y_global * 1.1) 
        ax_anim.grid(True)
        
        # Wrzucenie wykresu do placeholdera (nadpisuje poprzedni)
        plot_placeholder.pyplot(fig_anim)
        
        # BARDZO WAŻNE: Zamykamy figurę, żeby serwer nie wyczerpał pamięci RAM!
        plt.close(fig_anim) 
        
        # Pauza dla płynności
        time.sleep(delay)
        
    # Czyszczenie paska postępu na koniec
    progress_bar.empty()

st.markdown("---")
st.markdown("### 3. Mapa Bifurkacji (Fraktal)")
st.write("Wygenerowanie tej mapy wymaga policzenia tysięcy kombinacji. Kliknij przycisk poniżej, gdy będziesz gotowy.")








# MAPA BIRUKACJI
st.markdown("Dostosuj zakres parametrów Lambda i Beta oraz rozdzielczości mapy bifurkacji:")
col_b1, col_b2 = st.columns(2)
with col_b1:
    res_lambda = st.slider("Rozdzielczość Lambda (więcej = dłuższe liczenie)", 50, 300, 150, step=10)
with col_b2:
    res_beta = st.slider("Rozdzielczość Beta (więcej = dłuższe liczenie)", 50, 200, 100, step=10)


col_b3, col_b4 = st.columns(2)
with col_b3:
    l_min = st.number_input("Minimalna wartość Lambda", min_value=0.1, value=0.1, step=0.1)
    l_max = st.number_input("Maksymalna wartość Lambda", min_value=0.1, value=100.0, step=0.1)
with col_b4:
    b_min = st.number_input("Minimalna wartość Beta", min_value=0.1, value=0.1, step=0.1)
    b_max = st.number_input("Maksymalna wartość Beta", min_value=0.1, value=10.0, step=0.1)

if st.button("Generuj Mapę Bifurkacji 🚀"):
    with st.spinner("Liczenie fraktala... To może potrwać kilka sekund..."):
        l_vals, b_vals, Z = generate_bifurcation_heatmap(
            x0, 
            res_lambda=res_lambda, 
            res_beta=res_beta, 
            min_lambda=l_min, 
            max_lambda=l_max, 
            min_beta=b_min, 
            max_beta=b_max)
        
        fig_map, ax_map = plt.subplots(figsize=(12, 6))
        mesh = ax_map.pcolormesh(l_vals, b_vals, Z, cmap='turbo', shading='auto')
        cbar = plt.colorbar(mesh, ax=ax_map, ticks=[0, 1, 2, 3, 4, 5, 6])
        cbar.ax.set_yticklabels(['Stable', '2-cycle', '3-cycle', '4-cycle', '5-8', '8-16', 'Chaotic'])
        ax_map.set_xlabel("Lambda")
        ax_map.set_ylabel("Beta")
        
        st.pyplot(fig_map)
