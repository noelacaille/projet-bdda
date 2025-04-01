Projet TI603 BDDA

Noé LACAILLE
Lucas NGUYEN
Bily SASORITH
Clément WAWSZCZYK

### Run the Project

To start the development server, run:

```bash
npm run dev
```

### Admin Access

To access the admin panel and manage admin roles:

1. **Use the default admin account:**  
   - **Username:** `admin`  
   - **Password:** `Admin2024!`

2. **Alternatively, manually update the database:**  
   - Access the `users` table in the database.  
   - Change the `isAdmin` field from `0` to `1` for the desired user.  
   - This will grant the user admin privileges.

Once logged into the admin panel, any admin can manage the admin roles of other users.