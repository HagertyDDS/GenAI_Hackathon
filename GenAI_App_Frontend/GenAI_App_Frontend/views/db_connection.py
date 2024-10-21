# Database connection compoenent 

# Host 
# Port 
# Database Name 
# User 
# Password 
# CONNECT BUTTON


import reflex as rx



class DatabaseConnectionForm(rx.ComponentState):
    host: str = ""
    port: str = ""
    database: str = ""
    user: str = ""
    password: str = ""

    def connect(self):
        # Implement your database connection logic here
        pass

    @classmethod
    def get_component(cls, **props):
        return rx.vstack(
            rx.input(placeholder="Host", on_change=cls.set_host),
            rx.input(placeholder="Port", on_change=cls.set_port),
            rx.input(placeholder="Database Name", on_change=cls.set_database),
            rx.input(placeholder="User", on_change=cls.set_user),
            rx.input(placeholder="Password", type="password", on_change=cls.set_password),
            rx.button("Connect", on_click=cls.connect),
            **props
        )
    

def database_connection() -> rx.Component:
    return rx.vstack(
        rx.heading("Database Connection"),
        DatabaseConnectionForm.create()
    )