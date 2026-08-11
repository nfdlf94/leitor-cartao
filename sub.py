# -*- coding: utf-8 -*-
"""Subconjunto de DejaVu Sans com o que uma prova de matemática precisa."""
from fontTools import subset
import base64, os

BASICO = "".join(chr(c) for c in range(32,127))
PT = "ÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝàáâãäçèéêëìíîïñòóôõöùúûüýÿ"
MAT = (
 "ºª°±×÷¼½¾·‰′″"                        # ordinais, graus, frações
 "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾ⁿ"                      # expoentes
 "₀₁₂₃₄₅₆₇₈₉₊₋"                         # índices
 "∠⊥∥≅≃∼△▱⌒"                            # geometria: ângulo, perpendicular, paralelo
 "≠≈≡≤≥∞∝∴∵"                             # relações
 "∈∉∋⊂⊃⊆⊇∪∩∅∀∃¬∧∨"                       # conjuntos e lógica
 "√∛∜∫∑∏∆∇∂"                             # radicais, somatório, delta
 "αβγδεθλμπρσφωΑΒΓΔΘΛΠΣΦΩ"               # gregas usuais
 "→←↔⇒⇔↑↓"                               # setas
 "⌐¤§¶©®™†‡•…‹›«»“”‘’–—−"                # tipografia e sinais
 "▪■□▲△▼○●◦"                             # marcadores de figura
 "ℝℕℤℚ⋅∣≺≻"                              # conjuntos numéricos e relações
)
TEXTO = BASICO + PT + MAT

def fazer(origem, destino_js, nome_js, estilo):
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables += ["DSIG"]
    fonte = subset.load_font(origem, opts)
    sub = subset.Subsetter(options=opts)
    sub.populate(text=TEXTO)
    sub.subset(fonte)
    tmp = "/tmp/_sub.ttf"
    subset.save_font(fonte, tmp, opts)
    fonte.close()
    dados = open(tmp, "rb").read()
    b64 = base64.b64encode(dados).decode("ascii")
    return b64, len(dados)

pares = [("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "normal", "DBMSans-Regular.ttf"),
         ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "bold", "DBMSans-Bold.ttf")]
partes = ['/* fonte.js — DejaVu Sans reduzida ao que as provas usam.',
          '   Cobre acentuação portuguesa e os símbolos matemáticos comuns',
          '   (conjuntos, radicais, gregas, setas, expoentes).',
          '   Gerada por sub.py — não editar à mão. */',
          '"use strict";',
          'const DBM_FONTES = [']
total = 0
for caminho, estilo, arq in pares:
    b64, n = fazer(caminho, None, None, estilo)
    total += n
    partes.append('  {arquivo:"%s", estilo:"%s", dados:"%s"},' % (arq, estilo, b64))
    print("%-22s %6.1f KB  ->  base64 %6.1f KB" % (estilo, n/1024, len(b64)/1024))
partes.append('];')
partes.append('const DBM_COBERTURA = new Set(%s.map(c=>String.fromCodePoint(c)));'
               % __import__('json').dumps(sorted(ord(c) for c in set(TEXTO))))
partes.append('''
/* avisa antes de imprimir: caractere fora da fonte some da linha inteira */
function caracteresFaltando(textos){
  const fora = new Set();
  [].concat(textos).forEach(t => String(t==null?"":t).split("").forEach(c=>{
    if(c.charCodeAt(0) < 32) return;
    if(!DBM_COBERTURA.has(c)) fora.add(c);
  }));
  return [...fora];
}

function registrarFontes(doc){
  DBM_FONTES.forEach(f=>{
    doc.addFileToVFS(f.arquivo, f.dados);
    doc.addFont(f.arquivo, "DBMSans", f.estilo);
  });
  doc.setFont("DBMSans","normal");
  return doc;
}
if(typeof module!=="undefined") module.exports={DBM_FONTES, DBM_COBERTURA, caracteresFaltando, registrarFontes};''')
open("fonte.js","w",encoding="utf-8").write("\n".join(partes))
print("total ttf: %.1f KB | fonte.js: %.1f KB" % (total/1024, os.path.getsize("fonte.js")/1024))
