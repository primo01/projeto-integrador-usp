
## Configuração Inicial
Sete, primeiramente suas credencias do aws, sobreescrevendo os valores no `~/.aws/credentials`.
Apos, installe a CLI do terraform: https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

## Terraform Deployment

Para evitar possíveis problemas de alguem rodar mais de uma vez o script com o mesmo nome do bucket, foi criado um arquivo **terraform.tfvars.example**. Remova do nome do arquivo a palavra **.example**, e substitua o valor padrão *your-s3-bucket* pelo nome do seu bucket.

### Terminal (dentro da pasta raiz do projeto)
```bash
terraform init
terraform validate
terraform apply
```

> ⚠️ **ATENÇÃO**: NAO DELETE OS ARQUIVOS CRIADOS, senao vc tera de deletar tudo manualmente, e a gente sabe que ninguem quer isso :((((((

Quando estiver satisfeito com seu bom trabalho:
```bash
terraform destroy
```

---

## Carregamento da base no Postgres

Primeiramente remova o **.example** do arquivo **.env.example**, após isso configure as informações do bucket e de conexão com o banco de acordo com sua infra.

```bash
pip install -r requirements.txt
python3 load_taxi_zone_on_database.py
```

## Configuração do Airflow

Agora temos o Airflow numa EC2, da hora demais.
Para rodar esta maravilha criada pelos deuses, entre na pasta airflow.

### Criação da Chave SSH
Antes de tudo, certifique-se de criar uma chave publica usando o seguinte comando:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/airflow-key
```
Vuala, sua chave esta criada :)))))))))

### Deploy do Airflow
Agora, apos tanto esforco, rode, do seu terminal:
```bash
terraform init
terraform validate
terraform apply
```

### Conexão à Instância EC2
Assim que todos os recursos forem criados, ha a possibilidade de vc, muito provavelmente, querer logar na sua maquina EC2, desta forma, faca o seguinte:

1. Va ao console do AWS, e na barra de busca, procure por EC2.
2. Se vc for economico o suficiente, havera apenas uma instancia, com o nome de Airflow-EC2
3. Clique na caixinha ao lado esquerdo, e depois em connect, na direita superior.
4. Va na aba de SSH, e vc tera um url no seguinte formato:
   ```bash
   ssh -i "airflow-key.pem" ec2-user@ec2-40-221-11-249.compute-1.amazonaws.com
   ```
5. Copie o ip dessa lindeza: `ec2-40-221-11-249.compute-1.amazonaws.com`
6. Va na sua pasta .ssh, e execute:
   ```bash
   ssh -i ~/.ssh/airflow-key ec2-user@ec2-40-221-11-249.compute-1.amazonaws.com
   ```

### Rodando o Pyspark via Jupyter Notebook

#### Instalação do Pyspark e configução no Jupyter

```bash
wget https://downloads.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar -xvzf spark-3.5.0-bin-hadoop3.tgz
sudo mv spark-3.5.0-bin-hadoop3 /opt/spark

export SPARK_HOME=/opt/spark
export PATH=$SPARK_HOME/bin:$PATH
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS="notebook"
source ~/.bashrc
```

#### Rodando o pyspark

Primeiro faça o download localmente do **jar** do PostgresSQL

```bash
wget https://jdbc.postgresql.org/download/postgresql-42.5.1.jar -P ~/jars/
```

Depois rode passando os seguintes paramêtros:

```bash
pyspark --packages org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.11.901 --jars ~/jars/postgresql-42.5.1.jar
```

### Troubleshooting
Se vc tiver muitos problemas e quiser dar uma olhadinha nos logs (NAO RECOMENDADO, QUEM OLHA LOGS?):
```bash
cat /var/log/cloud-init-output.log
```

Alem disso, vc pode rodar o user-data, sem precisar reiniciar a maquina infinitas vezes, altere o script em:
```bash
/var/lib/cloud/instance/scripts/
```

Ai eh so dar um bash no nome do arquivo :)

Nao esquece do destroy quando terminar:

```terraform destroy```




## Airflow testing

- Adicionar script silver ao s3: aws s3 cp script_silver.py s3://taxi-raw-grupo-5/scripts/process_taxi_data.py

- Adicionar o emr-py para dentro do container airflow: docker cp emr-dag.py container_id:/opt/airflow/dags

- instalar aws cli dentro do container

```python -m pip install --upgrade pip```
```pip3 install awscli```

- Permissao do S3? Desativar encriptacao

- python -m pip install --upgrade pip

- set java version:

curl -L https://corretto.aws/downloads/latest/amazon-corretto-8-x64-linux-jdk.tar.gz -o corretto-8-linux.tar.gz

export JAVA_HOME=~/java/amazon-corretto-8.442.06.1-linux-x64/

export PATH=$JAVA_HOME/bin:$PATH

- Adicionar load_taxi_zone_on_database como dag no airflow :)





###### PARTE GABRIEL 
   Seguinte pessoal, vamos por partes, eu fiz um video explicando tudo então por favor assistam kkkk:

   https://jam.dev/c/4609a7cc-e21a-4d8c-a4a7-fad1bee8cf1b -- Video 1
   https://jam.dev/c/2f84bdcc-bfa2-4299-8f0d-9c89ecc59471 -- Video 2

   Resumindo:

      Pontos de atenção:
         Quase nenhum parametro da .env esta sendo utilizado, estou passando tudo na mão, então as mudanças do terraform, banco de dados etc estão sendo modificadas nos arquivos
         poderia usar o os.getenv() ? sim, uso? não.
         É necessário pegar e alterar o caminho do terraform, o comando para isso é ''' aws rds describe-db-instances '''
         É necessário alterar a versão do .jar para versão 45.5.1
         É necessário mudar nome do bucket, pois estou utilizando o nome já.
         É necessário rodar a criação do usuário no AIRFLOW na mão, pois não esta sendo criado automaticamente. ''' /airflow/user-data.sh  ultimas linhas '''
         É necessário tomar cuidado com o arquivo download-files.sh pois agora esta pegando o ano todo.
         É necessário subir os scripts direto na pasta DAGS, porque? pois eu não configurei para pegar direto da S3 e sim dos arquivos locais. Para conectar a S3 só mudar as
            configurações para ''' s3a://{bucket}/{folder name}/{script name}.py '''
         

      Erros comuns:
         Pode dar erro de digitação caso voce não passe o parametro correto ao referenciar o S3 o correto é s3a://
         Pode dar erro de arquivo .jar caso voce tente rodar mais de uma etapa dentro de uma dag, esse erro não é da versão do JAR é da DAG.
         Erro com o codigo 1 não são lidos pelo EMR / airflow, somente pelo YARN, e demora um pouco para aparecer, tenha paciencia.
         DAG não aparecer no airflow pode ser erro de nome de arquivo, verifica os nomes.
         Qualquer dependencia ou variavel de ambiente deve ser rodado direto no EC2, sem necessidade de rodar na imagem do docker, não lembro de rodar nada dentro do docker.


      Dicas:
         Tentem deixar o arquivo de DAGS com o mesmo nome da DAG, isso facilita o reconhecimento.
         Sempre validem o caminho do arquivo que a DAG esta pegando, exemplo, arquivo test.py linha 29 pega o arquivo chamado /opt/airflow/dags/taxi_data_processor.py
            então o script silver precisa ter esse nome, ou, voce muda o arquivo na dag para pegar do arquivo chamado script_silver.py.
            LEMBRANDO QUE PODE SER MODIFICADO PARA UM ARQUIVO S3 S3A://
         Se o REQUIREMENTS.TXT der erro, tente rodar na mão na EC2, nunca dentro do docker.
         A imagem do docker NÃO RODA NADA, quem roda é o EMR.
         Todas as dags tem a versão do JAR inputadas, verifica em todas se estão com a versão correta.
         
         



