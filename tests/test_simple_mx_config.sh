python -m prodxy.execution \
  --mx-config tests/simple_mx_config.yaml\
  --input 5\
  --parallelism 1\
  --variant a\
  --output tests/simple_a.jsonl

python -m prodxy.execution \
  --mx-config tests/simple_mx_config.yaml\
  --input tests/simple_a.jsonl\
  --parallelism 4\
  --variant b\
  --output tests/simple_b.jsonl

cat tests/simple_b.jsonl

read -n 1 -r -s -p "Press any key to continue..."

rm -f tests/simple_a.jsonl
rm -f tests/simple_b.jsonl

python -m prodxy.execution \
  --mx-config tests/simple_mx_config.yaml\
  --input 5\
  --parallelism 2\
  --variant a\
  --output tests/simple_a

python -m prodxy.execution \
  --mx-config tests/simple_mx_config.yaml\
  --input tests/simple_a\
  --parallelism 4\
  --variant b\
  --output tests/simple_b

cat tests/simple_b/*

read -n 1 -r -s -p "Press any key to continue..."

rm -rf tests/simple_a
rm -rf tests/simple_b