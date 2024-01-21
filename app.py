from src.flask_htmx_tailwind import create_app

if __name__ == "__main__":

    app = create_app()
    app.run(debug=True)