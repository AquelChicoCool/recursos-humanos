import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key-default")

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Decorador para proteger rutas autenticadas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Debes iniciar sesión para acceder.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session['user'] = {
                'id': res.user.id,
                'email': res.user.email
            }
            flash("Sesión iniciada con éxito.", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash("Credenciales inválidas. Verifica tu correo y contraseña.", "danger")
            return render_template('login.html', email=email)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    flash("Has cerrado sesión.", "info")
    return redirect(url_for('login'))

# --- DASHBOARD ---

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    res = supabase.table('empleados').select('*').execute()
    empleados = res.data if res.data else []

    total_empleados = len(empleados)
    activos = sum(1 for e in empleados if e.get('estado') == 'activo')
    inactivos = sum(1 for e in empleados if e.get('estado') == 'inactivo')

    # Desglose por departamento
    deptos = {}
    for e in empleados:
        dep = e.get('departamento', 'Sin Depto')
        deptos[dep] = deptos.get(dep, 0) + 1

    return render_template('dashboard.html', 
                           total=total_empleados, 
                           activos=activos, 
                           inactivos=inactivos, 
                           deptos=deptos)

# --- CRUD EMPLEADOS ---

@app.route('/empleados')
@login_required
def empleados():
    search = request.args.get('search', '').strip()
    depto_filter = request.args.get('departamento', '').strip()
    estado_filter = request.args.get('estado', '').strip()

    query = supabase.table('empleados').select('*')

    if estado_filter:
        query = query.eq('estado', estado_filter)
    if depto_filter:
        query = query.eq('departamento', depto_filter)

    res = query.order('created_at', desc=True).execute()
    lista_empleados = res.data if res.data else []

    # Filtrado local por nombre/apellido
    if search:
        s = search.lower()
        lista_empleados = [
            e for e in lista_empleados 
            if s in e.get('nombre', '').lower() or s in e.get('apellido', '').lower() or s in e.get('cargo', '').lower()
        ]

    # Obtener lista de departamentos para el selector de filtro
    all_res = supabase.table('empleados').select('departamento').execute()
    departamentos = sorted(list({e['departamento'] for e in all_res.data if e.get('departamento')})) if all_res.data else []

    return render_template('empleados.html', 
                           empleados=lista_empleados, 
                           search=search, 
                           depto_filter=depto_filter, 
                           estado_filter=estado_filter,
                           departamentos=departamentos)

@app.route('/empleados/crear', methods=['GET', 'POST'])
@login_required
def crear_empleado():
    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'email': request.form.get('email'),
            'rut': request.form.get('rut'),
            'cargo': request.form.get('cargo'),
            'departamento': request.form.get('departamento'),
            'fecha_ingreso': request.form.get('fecha_ingreso'),
            'estado': request.form.get('estado'),
            'telefono': request.form.get('telefono'),
            'observaciones': request.form.get('observaciones')
        }
        try:
            supabase.table('empleados').insert(data).execute()
            flash("Empleado registrado correctamente.", "success")
            return redirect(url_for('empleados'))
        except Exception as e:
            flash(f"Error al registrar empleado: {str(e)}", "danger")

    return render_template('crear_empleado.html')

@app.route('/empleados/editar/<id>', methods=['GET', 'POST'])
@login_required
def editar_empleado(id):
    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'apellido': request.form.get('apellido'),
            'email': request.form.get('email'),
            'rut': request.form.get('rut'),
            'cargo': request.form.get('cargo'),
            'departamento': request.form.get('departamento'),
            'fecha_ingreso': request.form.get('fecha_ingreso'),
            'estado': request.form.get('estado'),
            'telefono': request.form.get('telefono'),
            'observaciones': request.form.get('observaciones')
        }
        try:
            supabase.table('empleados').update(data).eq('id', id).execute()
            flash("Empleado actualizado correctamente.", "success")
            return redirect(url_for('empleados'))
        except Exception as e:
            flash(f"Error al actualizar empleado: {str(e)}", "danger")

    res = supabase.table('empleados').select('*').eq('id', id).execute()
    if not res.data:
        flash("Empleado no encontrado.", "warning")
        return redirect(url_for('empleados'))

    return render_template('editar_empleado.html', empleado=res.data[0])

@app.route('/empleados/eliminar/<id>', methods=['POST'])
@login_required
def eliminar_empleado(id):
    try:
        supabase.table('empleados').delete().eq('id', id).execute()
        return jsonify({'success': True, 'message': 'Empleado eliminado con éxito.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)