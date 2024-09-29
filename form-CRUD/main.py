import flet as ft
from contact_manager import ContactManager
from fpdf import FPDF
import pandas as pd
import datetime

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0,10,"Tabla de datos", 0, 1, "c")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0,10,f"Pagina {self.page_no()}", 0, 0, "C")
class Form(ft.UserControl):
    def __init__(self, page):
        super().__init__( expand=True)
        self.page = page
        self.data = ContactManager()
        self.selected_row = None

        self.name = ft.TextField(label = "Nombre", border_color = "blue")
        self.age = ft.TextField(label = "Edad", border_color = "blue", 
                                input_filter = ft.NumbersOnlyInputFilter(),
                                max_length=2)
        self.email = ft.TextField(label = "Correo", border_color = "blue")
        self.phone = ft.TextField(label = "Telefono", border_color = "blue",
                                  input_filter=ft.NumbersOnlyInputFilter(),
                                  max_length=10)
        self.search_field = ft.TextField(
            label = "Buscar por nombre",
            suffix_icon = ft.icons.SEARCH,
            border = ft.InputBorder.UNDERLINE,
            label_style = ft.TextStyle(color = "black"),
            on_change=self.search_data
        )
        self.data_table = ft.DataTable(
            expand=True,
            border = ft.border.all(2, "blue"),
            data_row_color={ft.MaterialState.SELECTED: "blue",
                            ft.MaterialState.PRESSED: "black"},
            border_radius=10,
            show_checkbox_column=True,
            columns=[
                ft.DataColumn(ft.Text("Nombre", color="blue", weight="bold")),
                ft.DataColumn(ft.Text("Edad", color="blue", weight="bold"),numeric=True),
                ft.DataColumn(ft.Text("Correo", color="blue", weight="bold")),
                ft.DataColumn(ft.Text("Telefono", color="blue", weight="bold"), numeric=True)
                
            ]
        )

        self.show_data()

        self.form = ft.Container(
            bgcolor = "#E2EAF4",
            border_radius = 10,
            col = 4,
            padding=10,
            content= ft.Column(
                alignment = ft.MainAxisAlignment.SPACE_AROUND,
                horizontal_alignment= ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Ingrese sus datos",
                            size = 24,
                            text_align="Center",
                            font_family="Open Sans"),
                    self.name,
                    self.age,
                    self.email,
                    self.phone,
                    ft.Container(
                        content=ft.Row(
                            spacing = 5,
                            alignment = ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.TextButton(text = "Guardar",
                                              icon = ft.icons.SAVE_AS,
                                              on_click = self.add_data),
                                ft.TextButton(text = "Actualizar",
                                              icon = ft.icons.UPDATE,
                                              on_click = self.updata_data),
                                ft.TextButton(text = "Borrar",
                                              icon = ft.icons.DELETE,
                                              on_click = self.delete_data)              
                            ]
                        )
                    ),
                  
                ]
            )
        )

        self.table = ft.Container(
            bgcolor = "#E7DDFF",
            border_radius = 10,
            col = 8,
            content= ft.Column(
                controls=[
                    ft.Container(
                        padding=10,
                        content=ft.Row(
                            controls = [
                                self.search_field,
                                ft.IconButton(tooltip="Editar",
                                              icon = ft.icons.EDIT,
                                              icon_color="black",
                                              on_click = self.edit_field_text),
                                ft.IconButton(tooltip="Descargar PDF",
                                              icon = ft.icons.PICTURE_AS_PDF,
                                              icon_color="black",
                                              on_click=self.save_pdf),
                                ft.IconButton(tooltip="Descargar EXCEL",
                                              icon = ft.icons.SAVE_ALT,
                                              icon_color="black",
                                              on_click=self.save_excel),
                            ]
                        )
                    ),
                      ft.Column(
                        expand=True,
                        scroll="auto",
                        controls=[
                            ft.ResponsiveRow([
                                self.data_table])
                        ]
                    )
                ]
            )
        )

        self.conent = ft.ResponsiveRow(
            controls = [
                self.form,
                self.table
            ]
        )
    
    #Función para mostrar los datos
    def show_data(self):
        self.data_table.rows = []
        for x in self.data.get_contacts():
            self.data_table.rows.append(
                ft.DataRow(
                    on_select_changed= self.get_index,
                    cells = [
                        ft.DataCell(ft.Text(x[1])),
                        ft.DataCell(ft.Text(str(x[2]))),
                        ft.DataCell(ft.Text(x[3])),
                        ft.DataCell(ft.Text(str(x[4])))
                    ]
                )
            )
        self.update()

    def add_data(self,e):
        name = self.name.value
        age = str(self.age.value)
        email = self.email.value
        phone = str(self.phone.value)

        if len(name) and len(age) and len(email) and len(phone)>0:
            contact_exist = False
            for row in self.data.get_contacts():
                if row[1]== name:
                    contact_exist = True
                    break
            if not contact_exist:
                self.clean_fields()
                self.data.add_contact(name,age,email,phone)
                self.show_data()
    
    def get_index(self,e):
        if e.control.selected:
            e.control.selected = False
        else:
            e.control.selected = True

        name = e.control.cells[0].content.value

        for row in self.data.get_contacts():
            if row[1] == name:
                self.selected_row = row
                break
        
        self.update()
    def edit_field_text(self,e):
        try:
            self.name.value = self.selected_row[1]
            self.age.value = self.selected_row[2]
            self.email.value = self.selected_row[3]
            self.phone.value = self.selected_row[4]
            self.update()
        except TypeError:
            print("Error")

    def updata_data(self, e):
        name = self.name.value
        age = str(self.age.value)
        email = self.email.value
        phone = str(self.phone.value)

        if len(name) and len(age) and len(email) and len(phone)>0:
            self.clean_fields()
            self.data.update_contact(self.selected_row[0], name, age, email, phone)
            self.show_data()
    def delete_data(self,e):
        self.data.delete_contact(self.selected_row[1])
        self.show_data()

    def search_data(self, e):
        search = self.search_field.value.lower()
        name = list( filter(lambda x:search in x[1].lower(), self.data.get_contacts()))
        self.data_table.rows = []
        if not self.search_field.value == '':
            if len(name)>0:
                for x in name:
                    self.data_table.rows.append(
                        ft.DataRow(
                            on_select_changed = self.get_index,
                            cells=[
                                ft.DataCell(ft.Text(x[1])),
                                ft.DataCell(ft.Text(str(x[2]))),
                                ft.DataCell(ft.Text(x[3])),
                                ft.DataCell(ft.Text(str(x[4]))),
                            ]
                        )
                    )
                    self.update()
        else:
            self.show_data()

    def clean_fields(self):
        self.name.value = ""
        self.age.value = ""
        self.email.value = ""
        self.phone.value = ""

    def save_pdf(self, e):
        pdf = PDF()
        pdf.add_page()
        column_widths = [10, 40, 20, 80, 40]
        data = self.data.get_contacts()
        header = ("ID", "NOMBRE", "EDAD", "CORREO", "TELEFONO")
        data.insert(0, header)
        for row in data:
            for item, width in zip(row, column_widths):
                pdf.cell(width, 10, str(item), border = 1)
            pdf.ln()
        
        file_name = datetime.datetime.now()
        file_name = file_name.strftime("DATA %Y-%m-%d_%H-%M-%S")+".pdf"
        pdf.output(file_name)

    def save_excel(self,e):
        file_name = datetime.datetime.now()
        file_name = file_name.strftime("DATA %Y-%m-%d_%H-%M-%S")+".xlsx"
        
        data = self.data.get_contacts()
        df = pd.DataFrame(data, columns=["ID", "NOMBRE", "EDAD", "CORREO", "TELEFONO"])
        df.to_excel(file_name, index=False)

    def build(self):
        return self.conent

def main(page: ft.Page):
    page.gbcolor= "black"
    page.title = "CRUD SQlite"
    page.window_min_height = 500
    page.window_min_width = 100

    page.add(Form(page))

ft.app(main)