#!/bin/bash

# Créez un tableau vide pour stocker les fichiers dans l'ordre correct
declare -a fileArray

# Parcourez tous les fichiers pcap dans le dossier
for file in *.pcap
do
  # Extrait le numéro du commentaire
  fileNumber=$(cat $file | grep -oP '(?<=//file)\d+')

  # Stocke le nom du fichier à l'index correspondant au numéro du commentaire
  fileArray[$fileNumber]=$file
done

# Concatène tous les fichiers dans l'ordre correct dans un nouveau fichier
for i in "${fileArray[@]}"
do
   cat "$i" >> combined_file.pcap
done
