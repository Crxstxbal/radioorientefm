from django import forms
from django.forms import ModelForm
from apps.emergente.models import BandaEmergente, BandaLink, Integrante, BandaIntegrante
from apps.ubicacion.models import Pais, Ciudad, Comuna
from apps.radio.models import Conductor

class BandaEmergenteForm(ModelForm):
    """Formulario para crear y editar bandas emergentes"""
    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all(),
        label='País',
        required=False,
        empty_label='Seleccione un país'
    )
    
    ciudad = forms.ModelChoiceField(
        queryset=Ciudad.objects.none(),
        label='Ciudad',
        required=False,
        empty_label='Primero seleccione un país'
    )
    
    comuna = forms.ModelChoiceField(
        queryset=Comuna.objects.none(),
        label='Comuna',
        required=False,
        empty_label='Primero seleccione una ciudad'
    )
    
    class Meta:
        model = BandaEmergente
        fields = [
            'nombre_banda', 'email_contacto', 'telefono_contacto', 
            'mensaje', 'documento_presentacion', 'genero', 'comuna'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si la instancia ya tiene una comuna, establecer la ciudad y país correspondientes
        if 'comuna' in self.data:
            try:
                comuna_id = int(self.data.get('comuna'))
                comuna = Comuna.objects.select_related('ciudad__pais').get(id=comuna_id)
                self.fields['comuna'].queryset = Comuna.objects.filter(ciudad=comuna.ciudad)
                self.fields['ciudad'].queryset = Ciudad.objects.filter(pais=comuna.ciudad.pais)
                self.fields['ciudad'].initial = comuna.ciudad
                self.fields['pais'].initial = comuna.ciudad.pais
            except (ValueError, Comuna.DoesNotExist):
                pass
        elif self.instance.pk and self.instance.comuna:
            comuna = self.instance.comuna
            self.fields['comuna'].queryset = Comuna.objects.filter(ciudad=comuna.ciudad)
            self.fields['ciudad'].queryset = Ciudad.objects.filter(pais=comuna.ciudad.pais)
            self.fields['ciudad'].initial = comuna.ciudad
            self.fields['pais'].initial = comuna.ciudad.pais
        
        # Establecer clases CSS para los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Hacer que el campo de mensaje sea un textarea
        self.fields['mensaje'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        
        # Hacer que el campo de género sea requerido
        self.fields['genero'].required = True
        self.fields['genero'].empty_label = 'Seleccione un género'
        
        # Hacer que los campos de ubicación sean requeridos en cascada
        if 'pais' in self.data and self.data['pais']:
            self.fields['ciudad'].required = True
            if 'ciudad' in self.data and self.data['ciudad']:
                self.fields['comuna'].required = True

class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        # Definimos los campos que queremos en el formulario
        fields = ['nombre', 'apellido', 'apodo', 'foto', 'email', 'telefono', 'activo']

        # Añadimos clases de Bootstrap a los campos para que se vean bien
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'apodo': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }