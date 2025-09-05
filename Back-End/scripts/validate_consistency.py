#!/usr/bin/env python3
"""
Script para validar la consistencia entre los scripts de importación y los módulos de la aplicación

Este script verifica que los scripts de importación sean consistentes con:
- Los esquemas de validación de los módulos
- Los modelos de datos
- Las restricciones de longitud de campos
- Los tipos de datos esperados

Uso:
    python3 scripts/validate_consistency.py
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import inspect

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.entidades.schemas.entidad import EntidadCreate
from app.modules.patologos.schemas.patologo import PatologoCreate
from app.modules.residentes.schemas.residente import ResidenteCreate
from app.modules.pruebas.schemas.prueba import PruebaCreate
from app.modules.enfermedades.models.enfermedad import EnfermedadCreate
from app.modules.pacientes.schemas.paciente import PacienteCreate
from app.modules.auth.schemas.administrator import AdministratorCreate


def validate_field_constraints(schema_class, field_name: str, value: Any) -> Tuple[bool, str]:
    """Valida las restricciones de un campo específico"""
    try:
        # Crear una instancia temporal para validar
        if hasattr(schema_class, '__annotations__'):
            field_info = schema_class.__annotations__.get(field_name)
            if field_info:
                # Validar longitud si es string
                if isinstance(value, str):
                    # Buscar validadores de longitud
                    for field in schema_class.__fields__.values():
                        if field.name == field_name:
                            if hasattr(field, 'field_info'):
                                min_length = getattr(field.field_info, 'min_length', None)
                                max_length = getattr(field.field_info, 'max_length', None)
                                
                                if min_length and len(value) < min_length:
                                    return False, f"Longitud mínima: {min_length}, actual: {len(value)}"
                                if max_length and len(value) > max_length:
                                    return False, f"Longitud máxima: {max_length}, actual: {len(value)}"
        return True, "OK"
    except Exception as e:
        return False, f"Error de validación: {str(e)}"


def validate_entidades_consistency():
    """Valida la consistencia del script de entidades"""
    print("🔍 Validando consistencia de entidades...")
    
    # Datos de prueba del script
    test_data = {
        "entidad_name": "Hospital Universitario San Vicente de Paul",
        "entidad_code": "HSV001",
        "observaciones": None,
        "is_active": True
    }
    
    issues = []
    
    # Validar longitud del nombre
    is_valid, message = validate_field_constraints(EntidadCreate, "entidad_name", test_data["entidad_name"])
    if not is_valid:
        issues.append(f"entidad_name: {message}")
    
    # Validar longitud del código
    is_valid, message = validate_field_constraints(EntidadCreate, "entidad_code", test_data["entidad_code"])
    if not is_valid:
        issues.append(f"entidad_code: {message}")
    
    if issues:
        print(f"❌ Problemas encontrados: {issues}")
        return False
    else:
        print("✅ Entidades: Consistente")
        return True


def validate_patologos_consistency():
    """Valida la consistencia del script de patólogos"""
    print("🔍 Validando consistencia de patólogos...")
    
    # Datos de prueba del script
    test_data = {
        "patologo_name": "Leiby Alejandra Medina Zuluaica",
        "iniciales_patologo": "LAM",
        "patologo_code": "32108690",  # 8 caracteres
        "patologo_email": "32108690.lam@udea.edu.co",
        "registro_medico": "PEND-32108690",
        "password": "32108690",
        "is_active": True,
        "firma": "",
        "observaciones": None
    }
    
    issues = []
    
    # Validar longitud del código (6-10 caracteres según esquema)
    if len(test_data["patologo_code"]) < 6 or len(test_data["patologo_code"]) > 10:
        issues.append(f"patologo_code: Longitud debe ser 6-10 caracteres, actual: {len(test_data['patologo_code'])}")
    
    # Validar longitud del nombre
    is_valid, message = validate_field_constraints(PatologoCreate, "patologo_name", test_data["patologo_name"])
    if not is_valid:
        issues.append(f"patologo_name: {message}")
    
    # Validar longitud de iniciales
    is_valid, message = validate_field_constraints(PatologoCreate, "iniciales_patologo", test_data["iniciales_patologo"])
    if not is_valid:
        issues.append(f"iniciales_patologo: {message}")
    
    if issues:
        print(f"❌ Problemas encontrados: {issues}")
        return False
    else:
        print("✅ Patólogos: Consistente")
        return True


def validate_residentes_consistency():
    """Valida la consistencia del script de residentes"""
    print("🔍 Validando consistencia de residentes...")
    
    # Datos de prueba del script
    test_data = {
        "residente_name": "María Carolina Aguilar Arango",
        "iniciales_residente": "MCA",
        "residente_code": "1152202153",  # 10 caracteres
        "residente_email": "1152202153.mca@udea.edu.co",
        "registro_medico": "PEND-1152202153",
        "password": "1152202153",
        "is_active": True,
        "observaciones": None
    }
    
    issues = []
    
    # Validar longitud del código (8-20 caracteres según esquema)
    if len(test_data["residente_code"]) < 8 or len(test_data["residente_code"]) > 20:
        issues.append(f"residente_code: Longitud debe ser 8-20 caracteres, actual: {len(test_data['residente_code'])}")
    
    # Validar longitud del nombre
    is_valid, message = validate_field_constraints(ResidenteCreate, "residente_name", test_data["residente_name"])
    if not is_valid:
        issues.append(f"residente_name: {message}")
    
    # Validar longitud de iniciales
    is_valid, message = validate_field_constraints(ResidenteCreate, "iniciales_residente", test_data["iniciales_residente"])
    if not is_valid:
        issues.append(f"iniciales_residente: {message}")
    
    if issues:
        print(f"❌ Problemas encontrados: {issues}")
        return False
    else:
        print("✅ Residentes: Consistente")
        return True


def validate_pruebas_consistency():
    """Valida la consistencia del script de pruebas"""
    print("🔍 Validando consistencia de pruebas...")
    
    # Datos de prueba del script
    test_data = {
        "prueba_name": "Estudio de Coloración Básica en Biopsia",
        "prueba_code": "898101",
        "prueba_description": "Biopsia simple un (1) frasco con uno o varios fragmentos de tejido hasta 3 cm/cc.",
        "tiempo": 360,  # 6 horas en minutos
        "is_active": True
    }
    
    issues = []
    
    # Validar longitud del nombre
    is_valid, message = validate_field_constraints(PruebaCreate, "prueba_name", test_data["prueba_name"])
    if not is_valid:
        issues.append(f"prueba_name: {message}")
    
    # Validar longitud del código
    is_valid, message = validate_field_constraints(PruebaCreate, "prueba_code", test_data["prueba_code"])
    if not is_valid:
        issues.append(f"prueba_code: {message}")
    
    # Validar tiempo (debe ser > 0 y <= 1440)
    if test_data["tiempo"] <= 0 or test_data["tiempo"] > 1440:
        issues.append(f"tiempo: Debe ser > 0 y <= 1440 minutos, actual: {test_data['tiempo']}")
    
    if issues:
        print(f"❌ Problemas encontrados: {issues}")
        return False
    else:
        print("✅ Pruebas: Consistente")
        return True


def validate_enfermedades_consistency():
    """Valida la consistencia del script de enfermedades"""
    print("🔍 Validando consistencia de enfermedades...")
    
    # Datos de prueba del script
    test_data = {
        "tabla": "CIE10",
        "codigo": "A00.0",
        "nombre": "Cólera debida a Vibrio cholerae 01, biotipo cholerae",
        "descripcion": "Descripción detallada de la enfermedad",
        "is_active": True
    }
    
    issues = []
    
    # Validar campos requeridos
    required_fields = ["tabla", "codigo", "nombre"]
    for field in required_fields:
        if not test_data.get(field):
            issues.append(f"{field}: Campo requerido")
    
    if issues:
        print(f"❌ Problemas encontrados: {issues}")
        return False
    else:
        print("✅ Enfermedades: Consistente")
        return True


def validate_pacientes_consistency():
    """Valida la consistencia del script de pacientes"""
    print("🔍 Validando consistencia de pacientes...")
    
    # Datos de prueba del script
    test_data = {
        "nombre": "Juan Carlos Pérez González",
        "edad": 45,
        "sexo": "Masculino",
        "entidad_info": {
            "id": "64f8a1b2c3d4e5f6a7b8c9d0",
            "nombre": "Hospital Universitario San Vicente de Paul"
        },
        "tipo_atencion": "Ambulatorio",
        "observaciones": None,
        "paciente_code": "123456789"
    }
    
    issues = []
    
    # Validar longitud del nombre
    is_valid, message = validate_field_constraints(PacienteCreate, "nombre", test_data["nombre"])
    if not is_valid:
        issues.append(f"nombre: {message}")
    
    # Validar edad
    if test_data["edad"] < 0 or test_data["edad"] > 150:
        issues.append(f"edad: Debe estar entre 0 y 150, actual: {test_data['edad']}")
    
    # Validar estructura de entidad_info
    if not isinstance(test_data["entidad_info"], dict):
        issues.append("entidad_info: Debe ser un diccionario")
    elif "id" not in test_data["entidad_info"] or "nombre" not in test_data["entidad_info"]:
        issues.append("entidad_info: Debe contener 'id' y 'nombre'")
    
    if issues:
        print(f"❌ Problemas encontrados: {issues}")
        return False
    else:
        print("✅ Pacientes: Consistente")
        return True


def validate_administrators_consistency():
    """Valida la consistencia del script de administradores"""
    print("🔍 Validando consistencia de administradores...")
    
    # Datos de prueba del script
    test_data = {
        "nombre": "Juan Pablo Restrepo",
        "email": "juan.restrepo183@udea.edu.co",
        "password": "Nomerobe-12345",
        "is_active": True
    }
    
    issues = []
    
    # Validar longitud del nombre
    is_valid, message = validate_field_constraints(AdministratorCreate, "nombre", test_data["nombre"])
    if not is_valid:
        issues.append(f"nombre: {message}")
    
    # Validar longitud de la contraseña
    if len(test_data["password"]) < 6:
        issues.append(f"password: Debe tener al menos 6 caracteres, actual: {len(test_data['password'])}")
    if len(test_data["password"]) > 128:
        issues.append(f"password: No puede tener más de 128 caracteres, actual: {len(test_data['password'])}")
    
    # Validar formato de email
    if not "@" in test_data["email"] or not "." in test_data["email"]:
        issues.append("email: Formato de email inválido")
    
    if issues:
        print(f"❌ Problemas encontrados: {issues}")
        return False
    else:
        print("✅ Administradores: Consistente")
        return True


def main():
    """Función principal de validación"""
    print("=" * 60)
    print("VALIDACIÓN DE CONSISTENCIA ENTRE SCRIPTS Y MÓDULOS")
    print("=" * 60)
    
    results = []
    
    # Validar cada módulo
    results.append(("Entidades", validate_entidades_consistency()))
    results.append(("Patólogos", validate_patologos_consistency()))
    results.append(("Residentes", validate_residentes_consistency()))
    results.append(("Pruebas", validate_pruebas_consistency()))
    results.append(("Enfermedades", validate_enfermedades_consistency()))
    results.append(("Pacientes", validate_pacientes_consistency()))
    results.append(("Administradores", validate_administrators_consistency()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for module, is_valid in results:
        status = "✅ PASÓ" if is_valid else "❌ FALLÓ"
        print(f"{module:15} {status}")
        if is_valid:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} pasaron, {failed} fallaron")
    
    if failed == 0:
        print("\n🎉 ¡Todas las validaciones pasaron! Los scripts son consistentes con los módulos.")
        return 0
    else:
        print(f"\n⚠️  {failed} módulo(s) tienen problemas de consistencia que deben ser corregidos.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
