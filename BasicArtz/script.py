import sqlite3

def change_user_role():
    
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()

  
    email = input("Ingrese el correo del usuario cuyo rol desea cambiar: ")

   
    cursor.execute("SELECT id, nombre, rol FROM usuarios WHERE mail = ?", (email,))
    user = cursor.fetchone()

    if not user:
        print("❌ Usuario no encontrado.")
        conn.close()
        return

    user_id, user_name, current_role = user
    print(f"📌 Usuario encontrado: {user_name} (Rol actual: {current_role})")

 
    new_role = input("Ingrese el nuevo rol ('admin' o 'user'): ").strip().lower()
    if new_role not in ['admin', 'user']:
        print("❌ Rol inválido. Usa 'admin' o 'user'.")
        conn.close()
        return

  
    cursor.execute("UPDATE usuarios SET rol = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

    print(f"✅ Rol cambiado con éxito. {user_name} ahora es '{new_role}'.")

if __name__ == "__main__":
    change_user_role()
