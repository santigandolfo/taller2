# taller2-app-server

[![Build Status](https://travis-ci.org/santigandolfo/taller2-app-server.svg?branch=master)](https://travis-ci.org/santigandolfo/taller2-app-server)

[![Coverage Status](https://coveralls.io/repos/github/santigandolfo/taller2-app-server/badge.svg?branch=master)](https://coveralls.io/github/santigandolfo/taller2-app-server?branch=master)



##Puesta en marcha local docker
Para setear las variables de entorno se debe hacer en el archivo .env, escribiendo en cada linea las distintas variables de entorno con el formato
NOMBRE=\"valor\".
Las variables a setear se encuentran en el archivo EnvVar.


Finalmente, ejecutar el comando:
> sh docker-correr-local.sh

##Subir a heroku docker container
```Heroku y docker debe estar instalado```
Para setear las variables de entorno se debe hacer en heroku, esto se puede hacer desde el dashboard desde la opcion Env Var.
Las variables a setear se encuentran en el archivo EnvVar.

Finalmente, ejecutar el comando:
> sh push\_docker\_to\_heroku.sh

##Puesta en marcha local heroku

```Heroku debe estar instalado```


Para setear las variables de entorno se debe ejecutar el comando 
> export \<NombreVariable\>=\"Valor\"
por cada variable de entorno necesaria.
Las variables a setear se encuentran en el archivo EnvVar.


Luego, ejecutar el comando en la misma shell donde se setearon las variables:
> heroku local


##Ejecutar las pruebas

``` Es necesario tener instalado mongodb y tener un servidor del mismo corriendo localmente```

Setear las variables de entorno acorde al archivo EnvVar, cabe destacar que las variables de entorno deben ser seteadas en la misma Shell donde se ejecutaran las pruebas. Para cada variable de entorno se debe ejecutar
> export \<NombreVariable\>=\"Valor\"

Para ejecutar las pruebas se debe ejecutar 

> python manage.py <comando-de-prueba>

Donde \<comando-de-prueba\> puede ser

 * *test* Ejecutar todas las pruebas **sin** coverage.
 * *cov* Ejecutar todas las pruebas **con** coverage.
 * *\<nombre-suite-especifica\>* Ejecuta los tests de la suite especifica, por ej. test_driver_manipulation
