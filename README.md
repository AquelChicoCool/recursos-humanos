1. Descargar el proyecto e instalar las dependencias
git clone https://github.com/Darklord25000/recursos-humanos.git
cd recursos-humanos
python -m venv venv


Activar el entorno virtual:
Windows: venv\Scripts\activate
macOS / Linux: source venv/bin/activate
pip install -r requeriments.txt



3. Preparar Supabase (lo hace una sola persona del equipo)
Crear un proyecto en supabase.com.
Ir a SQL Editor → New query, pegar el siguiente script y presionar Run. Crea la tabla empleados con los campos que usa la aplicación:
sql
create table empleados (
  id uuid primary key default gen_random_uuid(),
  nombre text not null,
  apellido text not null,
  email text,
  rut text,
  cargo text,
  departamento text,
  fecha_ingreso date,
  estado text default 'activo',   -- 'activo' o 'inactivo'
  telefono text,
  observaciones text,
  created_at timestamptz default now()


Ir a Authentication → Users → Add user → Create new user y crear al menos una cuenta marcando Auto Confirm User (por ejemplo rrhh@empresa-demo.cl). Con ese correo y contraseña se inicia sesión en el sistema.


En Project Settings → API Keys (o con el botón Connect), copiar la Project URL y la clave anon / publishable.

⚠️ Nunca usen la clave service_role / secret.


3. Crear el archivo .env
Copiar .env.example con el nombre .env y completar los valores:
SECRET_KEY=una_clave_larga_y_aleatoria
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_KEY=clave_anon_o_publishable
Para generar SECRET_KEY: python -c "import secrets; print(secrets.token_hex(32))"

El archivo .env no se sube a GitHub porque está en .gitignore.

5. Ejecutar
python app.py
Abrir http://127.0.0.1:5000 e ingresar con la cuenta creada en Supabase. Al entrar se llega al Dashboard, que muestra el total de empleados, activos e inactivos y el desglose por departamento. Desde el menú Empleados se puede buscar (por nombre, apellido o cargo), filtrar por departamento y estado, registrar,
editar y eliminar empleados.


Para que otra persona pueda entrar al sistema, hay que crearle una cuenta en Supabase (Authentication → Users).

Seguridad dentro del sistema
Para usar cualquier página hay que iniciar sesión; si no, el sistema redirige al login.
La sesión se guarda con una SECRET_KEY propia y se cierra completamente al presionar Cerrar Sesión.
Se pide confirmación (SweetAlert) antes de eliminar un empleado.
Los errores de login, registro, edición y eliminación se informan al usuario con mensajes claros.
Las claves solo están en .env. En GitHub se sube únicamente .env.example.
Como es un proyecto de prueba con datos ficticios, la base de datos no tiene protección adicional (sin políticas RLS).
