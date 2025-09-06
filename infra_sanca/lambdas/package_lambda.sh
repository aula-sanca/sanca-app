#!/bin/bash
set -e

SRC_DIR="src"

echo "Empaquetando Lambdas desde $SRC_DIR ..."

for dir in $SRC_DIR/*/ ; do
  # quitar la barra final y quedarnos con el nombre
  echo "dir $dir ..."
  lambda_name=$(basename "$dir")

  # Eliminar zip previo si existe
  if [ -f "$lambda_name" ]; then
    echo "Elminando zip previo $lambda_name ..."
    rm "$lambda_name"
  fi

  echo "Empaquetando $lambda_name ..."

  cd "$dir"
  zip -r "${lambda_name}.zip" . > /dev/null
  cd - > /dev/null
done

echo "Todas las Lambdas fueron empaquetadas!"
