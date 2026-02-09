from django import forms

from .models import Equipo


class EquipoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["numero_inventario"].required = True

    class Meta:
        model = Equipo
        fields = [
            "centro_costo",
            "identificador",
            "nombre",
            "numero_serie",
            "clave",
            "numero_inventario",
            "marca",
            "modelo",
            "tipo_equipo",
            "sistema_operativo",
            "direccion_ip",
            "direccion_mac",
            "entidad",
            "municipio",
            "domicilio",
            "codigo_postal",
            "antiguedad",
            "rpe_responsable",
            "nombre_responsable",
            "infraestructura_critica",
        ]
        widgets = {
            "centro_costo": forms.Select(attrs={"class": "form-select"}),
            "identificador": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "numero_serie": forms.TextInput(attrs={"class": "form-control"}),
            "clave": forms.TextInput(attrs={"class": "form-control"}),
            "numero_inventario": forms.TextInput(attrs={"class": "form-control"}),
            "marca": forms.Select(attrs={"class": "form-select"}),
            "modelo": forms.Select(attrs={"class": "form-select"}),
            "tipo_equipo": forms.Select(attrs={"class": "form-select"}),
            "sistema_operativo": forms.Select(attrs={"class": "form-select"}),
            "direccion_ip": forms.TextInput(attrs={"class": "form-control"}),
            "direccion_mac": forms.TextInput(attrs={"class": "form-control"}),
            "entidad": forms.TextInput(attrs={"class": "form-control"}),
            "municipio": forms.TextInput(attrs={"class": "form-control"}),
            "domicilio": forms.TextInput(attrs={"class": "form-control"}),
            "codigo_postal": forms.TextInput(attrs={"class": "form-control"}),
            "antiguedad": forms.TextInput(attrs={"class": "form-control"}),
            "rpe_responsable": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_responsable": forms.TextInput(attrs={"class": "form-control"}),
            "infraestructura_critica": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
