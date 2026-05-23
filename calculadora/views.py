from django.shortcuts import render
import math

# --- LOGIC DE MÉTODOS NUMÉRICOS ---

def metodo_taylor(funcion_str, x, a, n):
    """
    Simulación simplificada de la Serie de Taylor para funciones comunes evaluadas dinámicamente.
    Para un proyecto real avanzado, se suele usar la librería 'sympy'.
    """
    # Ejemplo básico usando aproximación exponencial con fines ilustrativos
    aproximacion = 0.0
    historial = []
    
    for i in range(int(n) + 1):
        # f^(i)(a) para e^x sigue siendo e^a
        if funcion_str.lower() == 'e^x':
            derivada_en_a = math.exp(a)
        else:
            derivada_en_a = 1.0 # Valor por defecto/lineal si es otra función
            
        termino = (derivada_en_a / math.factorial(i)) * ((x - a) ** i)
        aproximacion += termino
        historial.append({'iteracion': i, 'termino': termino, 'acumulado': aproximacion})
        
    return aproximacion, historial


def f(x, funcion_str):
    """Evalúa funciones matemáticas típicas de examen de forma segura."""
    # Reemplazos comunes para que Python los entienda
    diccionario_seguro = {
        'x': x,
        'math': math,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'exp': math.exp,
        'log': math.log,
        'pi': math.pi
    }
    # Reemplazar la notación de potencia ^ por ** de Python
    funcion_python = funcion_str.replace('^', '**')
    try:
        return eval(funcion_python, {"__builtins__": None}, diccionario_seguro)
    except:
        return None

def m_derivada(x, funcion_str, h=1e-5):
    """Aproximación numérica de la primera derivada."""
    fx_mas_h = f(x + h, funcion_str)
    fx_menos_h = f(x - h, funcion_str)
    if fx_mas_h is not None and fx_menos_h is not None:
        return (fx_mas_h - fx_menos_h) / (2 * h)
    return None

def m_segunda_derivada(x, funcion_str, h=1e-5):
    """Aproximación numérica de la segunda derivada (necesaria para el Modificado)."""
    fx_mas_h = f(x + h, funcion_str)
    fx = f(x, funcion_str)
    fx_menos_h = f(x - h, funcion_str)
    if fx_mas_h is not None and fx is not None and fx_menos_h is not None:
        return (fx_mas_h - 2*fx + fx_menos_h) / (h**2)
    return None


def metodo_newton_raphson(funcion_str, x0, tol, max_iter, modificado=False):
    historial = []
    x_act = float(x0)
    error = 100.0
    iteracion = 0
    
    while error > float(tol) and iteracion < int(max_iter):
        fx = f(x_act, funcion_str)
        d1 = m_derivada(x_act, funcion_str)
        
        if fx is None or d1 == 0 or d1 is None:
            break
            
        if modificado:
            d2 = m_segunda_derivada(x_act, funcion_str)
            if d2 is None or (d1**2 - fx*d2) == 0:
                break
            # Fórmula de Newton-Raphson Modificado para raíces múltiples
            x_sig = x_act - (fx * d1) / (d1**2 - fx * d2)
        else:
            # Fórmula estándar de Newton-Raphson
            x_sig = x_act - (fx / d1)
            
        error = abs((x_sig - x_act) / x_sig) * 100 if x_sig != 0 else 0.0
        
        historial.append({
            'iteracion': iteracion + 1,
            'x_ant': x_act,
            'fx': fx,
            'd1': d1,
            'x_sig': x_sig,
            'error': error
        })
        
        x_act = x_sig
        iteracion += 1
        
    return x_act, historial

# --- VISTAS DE DJANGO ---

def home(request):
    contexto = {}
    if request.method == 'POST':
        tipo_metodo = request.POST.get('tipo_metodo')
        funcion = request.POST.get('funcion', 'x^2 - 4')
        
        if tipo_metodo == 'taylor':
            x = float(request.POST.get('taylor_x', 1))
            a = float(request.POST.get('taylor_a', 0))
            n = int(request.POST.get('taylor_n', 4))
            resultado, historial = metodo_taylor(funcion, x, a, n)
            contexto = {'resultado': resultado, 'historial': historial, 'metodo': 'Taylor', 'funcion': funcion}
            
        elif tipo_metodo in ['newton', 'newton_mod']:
            x0 = float(request.POST.get('newton_x0', 1))
            tol = float(request.POST.get('newton_tol', 0.001))
            max_iter = int(request.POST.get('newton_iter', 20))
            mod = (tipo_metodo == 'newton_mod')
            
            resultado, historial = metodo_newton_raphson(funcion, x0, tol, max_iter, modificado=mod)
            nombre = "Newton-Raphson Modificado" if mod else "Newton-Raphson Tradicional"
            contexto = {'resultado': resultado, 'historial': historial, 'metodo': nombre, 'funcion': funcion}

    return render(request, 'calculadora/index.html', contexto)