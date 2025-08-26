// Script de inicialización para MongoDB
// Este script se ejecuta cuando se crea la base de datos por primera vez

// Usar la base de datos lime_pathsys
db = db.getSiblingDB('lime_pathsys');

// Crear colecciones con validación de esquemas

// Colección de usuarios
db.createCollection('usuarios', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['nombre', 'email', 'rol', 'password_hash', 'is_active'],
      properties: {
        nombre: {
          bsonType: 'string',
          description: 'Nombre completo del usuario'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
          description: 'Email válido del usuario'
        },
        rol: {
          bsonType: 'string',
          enum: ['administrador', 'auxiliar', 'patologo', 'residente', 'paciente'],
          description: 'Rol del usuario'
        },
        password_hash: {
          bsonType: 'string',
          description: 'Hash de la contraseña'
        },
        is_active: {
          bsonType: 'bool',
          description: 'Estado activo del usuario'
        },
        fecha_creacion: {
          bsonType: 'date',
          description: 'Fecha de creación'
        },
        fecha_actualizacion: {
          bsonType: 'date',
          description: 'Fecha de última actualización'
        }
      }
    }
  }
});

// Crear índices para usuarios
db.usuarios.createIndex({ 'email': 1 }, { unique: true });
db.usuarios.createIndex({ 'rol': 1 });
db.usuarios.createIndex({ 'is_active': 1 });

// Colección de pacientes
db.createCollection('pacientes', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['numeroCedula', 'nombre', 'apellido'],
      properties: {
        numeroCedula: {
          bsonType: 'string',
          description: 'Número de cédula único'
        },
        nombre: {
          bsonType: 'string',
          description: 'Nombre del paciente'
        },
        apellido: {
          bsonType: 'string',
          description: 'Apellido del paciente'
        },
        fechaNacimiento: {
          bsonType: 'date',
          description: 'Fecha de nacimiento'
        },
        telefono: {
          bsonType: 'string',
          description: 'Teléfono del paciente'
        },
        email: {
          bsonType: 'string',
          description: 'Email del paciente'
        },
        direccion: {
          bsonType: 'string',
          description: 'Dirección del paciente'
        }
      }
    }
  }
});

// Crear índices para pacientes
db.pacientes.createIndex({ 'numeroCedula': 1 }, { unique: true });
db.pacientes.createIndex({ 'nombre': 1, 'apellido': 1 });

// Colección de casos - CORREGIDO: usar CasoCode en lugar de codigoCaso
db.createCollection('casos');
db.casos.createIndex({ 'CasoCode': 1 }, { unique: true });
db.casos.createIndex({ 'paciente.codigo': 1 });
// Índices relevantes
db.casos.createIndex({ 'fecha_entrega': 1 });
db.casos.createIndex({ 'estado': 1 });

// Colección de patólogos
db.createCollection('patologos');
db.patologos.createIndex({ 'documento': 1 }, { unique: true });
db.patologos.createIndex({ 'email': 1 }, { unique: true });
db.patologos.createIndex({ 'medicalLicense': 1 }, { unique: true });

// Colección de residentes
db.createCollection('residentes');
db.residentes.createIndex({ 'documento': 1 }, { unique: true });
db.residentes.createIndex({ 'email': 1 }, { unique: true });
db.residentes.createIndex({ 'codigo_residente': 1 }, { unique: true });

// Colección de entidades
db.createCollection('entidades');
db.entidades.createIndex({ 'entityName': 1 }, { unique: true });
db.entidades.createIndex({ 'nit': 1 }, { unique: true });

// Colección de pruebas
db.createCollection('pruebas');
db.pruebas.createIndex({ 'nombre': 1 });
db.pruebas.createIndex({ 'categoria': 1 });

// Colección de contadores
db.createCollection('contadores');
db.contadores.createIndex({ 'año': 1 }, { unique: true });

print('Base de datos inicializada correctamente con colecciones e índices');