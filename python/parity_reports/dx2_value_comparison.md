# DX2 MATLAB vs Python Values

## dx2abck (3 cases)

### Case c1 - base

### A

MATLAB fixture:
```text
[[ 0.715402817   0.0979231485]
 [-0.0749896674  0.6422634985]]
```
Python generated:
```text
[[ 0.715402817   0.0979231485]
 [-0.0749896674  0.6422634985]]
```
Absolute difference |Python - MATLAB|:
```text
[[8.8817841970e-16 5.5511151231e-17]
 [1.8041124150e-16 1.1102230246e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[1.2415081387e-13 5.6688486934e-14]
 [2.4058146638e-13 1.7286098731e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.2415081387e-13 5.6688486934e-14]
 [2.4058146638e-13 1.7286098731e-14]]
```

### B

MATLAB fixture:
```text
[[ 0.0941010038]
 [-0.2909688847]]
```
Python generated:
```text
[[ 0.0941010038]
 [-0.2909688847]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.8041124150e-16]
 [1.1102230246e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[1.9172084707e-13]
 [3.8156073825e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.9172084707e-13]
 [3.8156073825e-14]]
```

### C

MATLAB fixture:
```text
[[-0.3870264566  0.1686944782]]
```
Python generated:
```text
[[-0.3870264566  0.1686944782]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.7755575616e-16 2.7755575616e-17]]
```
difference / abs(matlab_value) * 100:
```text
[[7.1714930953e-14 1.6453161901e-14]]
```
difference / abs(python_value) * 100:
```text
[[7.1714930953e-14 1.6453161901e-14]]
```

### K

MATLAB fixture:
```text
[[ 0.1123384391]
 [-0.1224343125]]
```
Python generated:
```text
[[ 0.1123384391]
 [-0.1224343125]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.7061686225e-15]
 [6.8001160258e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[2.4089426947e-12]
 [5.5540933652e-13]]
```
difference / abs(python_value) * 100:
```text
[[2.4089426947e-12]
 [5.5540933652e-13]]
```

### Case c1 - stable1

### A

MATLAB fixture:
```text
[[ 0.3912629536  0.0981600764]
 [-1.7838874967  1.1968559911]]
```
Python generated:
```text
[[ 0.3912626386  0.0981601916]
 [-1.7838879882  1.1968563061]]
```
Absolute difference |Python - MATLAB|:
```text
[[3.1503767178e-07 1.1522189831e-07]
 [4.9151344461e-07 3.1503316533e-07]]
```
difference / abs(matlab_value) * 100:
```text
[[8.0518144859e-05 1.1738163065e-04]
 [2.7552939606e-05 2.6321726898e-05]]
```
difference / abs(python_value) * 100:
```text
[[8.0518209691e-05 1.1738149286e-04]
 [2.7552932015e-05 2.6321719970e-05]]
```

### B

MATLAB fixture:
```text
[[2.8928792213e+10]
 [7.0815270036e+10]]
```
Python generated:
```text
[[2.8914947767e+10]
 [7.0781368890e+10]]
```
Absolute difference |Python - MATLAB|:
```text
[[13844446.11524582]
 [33901146.0431366 ]]
```
difference / abs(matlab_value) * 100:
```text
[[0.0478569793]
 [0.0478726495]]
```
difference / abs(python_value) * 100:
```text
[[0.0478798932]
 [0.0478955784]]
```

### C

MATLAB fixture:
```text
[[-0.3241901914  0.2117425166]]
```
Python generated:
```text
[[-0.3241901914  0.2117425155]]
```
Absolute difference |Python - MATLAB|:
```text
[[5.5511151231e-17 1.0897948655e-09]]
```
difference / abs(matlab_value) * 100:
```text
[[1.7123019975e-14 5.1467928261e-07]]
```
difference / abs(python_value) * 100:
```text
[[1.7123019975e-14 5.1467928526e-07]]
```

### K

MATLAB fixture:
```text
[[1.0414576075]
 [5.7042390205]]
```
Python generated:
```text
[[1.0414586149]
 [5.7042405922]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.0073639072e-06]
 [1.5716943080e-06]]
```
difference / abs(matlab_value) * 100:
```text
[[9.6726347759e-05]
 [2.7553093452e-05]]
```
difference / abs(python_value) * 100:
```text
[[9.6726254199e-05]
 [2.7553085860e-05]]
```

### Case c2 - base

### A

MATLAB fixture:
```text
[[ 0.7204834087  0.0996598553]
 [-0.0784131085  0.638883403 ]]
```
Python generated:
```text
[[ 0.7204834087  0.0996598553]
 [-0.0784131085  0.638883403 ]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.1102230246e-16 2.0816681712e-16]
 [1.4988010832e-15 3.3306690739e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[1.5409418333e-14 2.0887730211e-13]
 [1.9114164866e-12 5.2132659235e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.5409418333e-14 2.0887730211e-13]
 [1.9114164866e-12 5.2132659235e-14]]
```

### B

MATLAB fixture:
```text
[[ 0.1005578579]
 [-0.421541744 ]]
```
Python generated:
```text
[[ 0.1005578579]
 [-0.421541744 ]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.2490009027e-16]
 [5.5511151231e-17]]
```
difference / abs(matlab_value) * 100:
```text
[[1.2420719070e-13]
 [1.3168601216e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.2420719070e-13]
 [1.3168601216e-14]]
```

### C

MATLAB fixture:
```text
[[-0.1450720991  0.2682238463]]
```
Python generated:
```text
[[-0.1450720991  0.2682238463]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.7755575616e-16 0.0000000000e+00]]
```
difference / abs(matlab_value) * 100:
```text
[[1.9132263048e-13 0.0000000000e+00]]
```
difference / abs(python_value) * 100:
```text
[[1.9132263048e-13 0.0000000000e+00]]
```

### K

MATLAB fixture:
```text
[[0.0859200768]
 [0.2820508825]]
```
Python generated:
```text
[[0.0859200768]
 [0.2820508825]]
```
Absolute difference |Python - MATLAB|:
```text
[[3.2612801348e-15]
 [1.4432899320e-15]]
```
difference / abs(matlab_value) * 100:
```text
[[3.7957137122e-12]
 [5.1171260981e-13]]
```
difference / abs(python_value) * 100:
```text
[[3.7957137122e-12]
 [5.1171260981e-13]]
```

### Case c2 - stable1

### A

MATLAB fixture:
```text
[[-1.1506278798 -1.3352299786]
 [ 2.841960517   2.738747061 ]]
```
Python generated:
```text
[[-1.1506278248 -1.3352299192]
 [ 2.8419604833  2.738747006 ]]
```
Absolute difference |Python - MATLAB|:
```text
[[5.4975234809e-08 5.9387293749e-08]
 [3.3723795312e-08 5.4968442242e-08]]
```
difference / abs(matlab_value) * 100:
```text
[[4.7778465805e-06 4.4477202207e-06]
 [1.1866384178e-06 2.0070653119e-06]]
```
difference / abs(python_value) * 100:
```text
[[4.7778468088e-06 4.4477204185e-06]
 [1.1866384318e-06 2.0070653522e-06]]
```

### B

MATLAB fixture:
```text
[[-7.4781591303e+08]
 [ 9.3598044780e+08]]
```
Python generated:
```text
[[-7.4807483181e+08]
 [ 9.3630452696e+08]]
```
Absolute difference |Python - MATLAB|:
```text
[[258918.7749150991]
 [324079.1622475386]]
```
difference / abs(matlab_value) * 100:
```text
[[0.0346233305]
 [0.0346245654]]
```
difference / abs(python_value) * 100:
```text
[[0.0346113469]
 [0.0346125809]]
```

### C

MATLAB fixture:
```text
[[-0.2766541432 -0.263518637 ]]
```
Python generated:
```text
[[-0.2766541432 -0.2635186348]]
```
Absolute difference |Python - MATLAB|:
```text
[[0.0000000000e+00 2.2237581221e-09]]
```
difference / abs(matlab_value) * 100:
```text
[[0.000000000e+00 8.438712901e-07]]
```
difference / abs(python_value) * 100:
```text
[[0.0000000000e+00 8.4387129722e-07]]
```

### K

MATLAB fixture:
```text
[[  6.9979939198]
 [-10.649052015 ]]
```
Python generated:
```text
[[  6.9979937141]
 [-10.6490518887]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.0570310078e-07]
 [1.2635319990e-07]]
```
difference / abs(matlab_value) * 100:
```text
[[2.9394581237e-06]
 [1.1865206379e-06]]
```
difference / abs(python_value) * 100:
```text
[[2.9394582102e-06]
 [1.1865206520e-06]]
```

### Case c3 - base

### A

MATLAB fixture:
```text
[[ 0.7178872811  0.0972181758]
 [-0.0802037176  0.6397317644]]
```
Python generated:
```text
[[ 0.7178872811  0.0972181758]
 [-0.0802037176  0.6397317644]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.1102230246e-15 5.8286708793e-16]
 [2.4424906542e-15 1.9984014443e-15]]
```
difference / abs(matlab_value) * 100:
```text
[[1.5465144095e-13 5.9954538676e-13]
 [3.0453584047e-12 3.1238115029e-13]]
```
difference / abs(python_value) * 100:
```text
[[1.5465144095e-13 5.9954538676e-13]
 [3.0453584047e-12 3.1238115029e-13]]
```

### B

MATLAB fixture:
```text
[[ 0.0892635201]
 [-0.1471096576]]
```
Python generated:
```text
[[ 0.0892635201]
 [-0.1471096576]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.9428902931e-16]
 [8.3266726847e-17]]
```
difference / abs(matlab_value) * 100:
```text
[[2.1765781711e-13]
 [5.6601808595e-14]]
```
difference / abs(python_value) * 100:
```text
[[2.1765781711e-13]
 [5.6601808595e-14]]
```

### C

MATLAB fixture:
```text
[[-0.2130122451 -0.4954665883]]
```
Python generated:
```text
[[-0.2130122451 -0.4954665883]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.4980018054e-16 1.6653345369e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[1.1727033835e-13 3.3611439728e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.1727033835e-13 3.3611439728e-14]]
```

### K

MATLAB fixture:
```text
[[0.0791980853]
 [0.0076366251]]
```
Python generated:
```text
[[0.0791980853]
 [0.0076366251]]
```
Absolute difference |Python - MATLAB|:
```text
[[4.7600812181e-15]
 [2.2022314528e-15]]
```
difference / abs(matlab_value) * 100:
```text
[[6.0103488589e-12]
 [2.8837758013e-11]]
```
difference / abs(python_value) * 100:
```text
[[6.0103488589e-12]
 [2.8837758013e-11]]
```

### Case c3 - stable1

### A

MATLAB fixture:
```text
[[ 1.3346354138  0.0661309523]
 [-4.6133362368  0.2534824416]]
```
Python generated:
```text
[[ 1.3346344679  0.0661303611]
 [-4.613362016   0.2534833874]]
```
Absolute difference |Python - MATLAB|:
```text
[[9.4591318289e-07 5.9120635203e-07]
 [2.5779245943e-05 9.4583686888e-07]]
```
difference / abs(matlab_value) * 100:
```text
[[7.0874275708e-05 8.9399340486e-04]
 [5.5879833206e-04 3.7313703581e-04]]
```
difference / abs(python_value) * 100:
```text
[[7.0874325940e-05 8.9400139717e-04]
 [5.5879520952e-04 3.7313564350e-04]]
```

### B

MATLAB fixture:
```text
[[ 4.0037194461e+08]
 [-8.6055249199e+09]]
```
Python generated:
```text
[[ 4.0047895329e+08]
 [-8.6079109820e+09]]
```
Absolute difference |Python - MATLAB|:
```text
[[ 107008.6842368245]
 [2386062.0828533173]]
```
difference / abs(matlab_value) * 100:
```text
[[0.0267273184]
 [0.0277270952]]
```
difference / abs(python_value) * 100:
```text
[[0.0267201768]
 [0.0277194094]]
```

### C

MATLAB fixture:
```text
[[-0.3763789527  0.0180922486]]
```
Python generated:
```text
[[-0.3763789527  0.0180922247]]
```
Absolute difference |Python - MATLAB|:
```text
[[0.0000000000e+00 2.3934841574e-08]]
```
difference / abs(matlab_value) * 100:
```text
[[0.           0.0001322933]]
```
difference / abs(python_value) * 100:
```text
[[0.           0.0001322935]]
```

### K

MATLAB fixture:
```text
[[-1.701245984 ]
 [12.7063284098]]
```
Python generated:
```text
[[-1.7012433789]
 [12.7063994129]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.6050995008e-06]
 [7.1003104388e-05]]
```
difference / abs(matlab_value) * 100:
```text
[[0.0001531289]
 [0.0005588011]]
```
difference / abs(python_value) * 100:
```text
[[0.0001531291]
 [0.000558798 ]]
```

## dx2abcdk (3 cases)

### Case c1 - base

### A

MATLAB fixture:
```text
[[ 0.7198294717  0.1002559066]
 [-0.0795069604  0.6392601107]]
```
Python generated:
```text
[[ 0.7198294717  0.1002559066]
 [-0.0795069604  0.6392601107]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.2204460493e-16 2.0816681712e-16]
 [8.4654505628e-16 1.1102230246e-15]]
```
difference / abs(matlab_value) * 100:
```text
[[3.0846834377e-14 2.0763546431e-13]
 [1.0647433287e-12 1.7367312712e-13]]
```
difference / abs(python_value) * 100:
```text
[[3.0846834377e-14 2.0763546431e-13]
 [1.0647433287e-12 1.7367312712e-13]]
```

### B

MATLAB fixture:
```text
[[-0.1871679391]
 [-0.2235556901]]
```
Python generated:
```text
[[-0.1871679391]
 [-0.2235556901]]
```
Absolute difference |Python - MATLAB|:
```text
[[5.5511151231e-17]
 [1.1102230246e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[2.9658472221e-14]
 [4.9662033846e-14]]
```
difference / abs(python_value) * 100:
```text
[[2.9658472221e-14]
 [4.9662033846e-14]]
```

### C

MATLAB fixture:
```text
[[ 0.1226145547 -0.6198992161]]
```
Python generated:
```text
[[ 0.1226145547 -0.6198992161]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.2490009027e-16 1.1102230246e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[1.0186400025e-13 1.7909734288e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.0186400025e-13 1.7909734288e-14]]
```

### D

MATLAB fixture:
```text
[[-0.1022403927]]
```
Python generated:
```text
[[-0.1022403927]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.3877787808e-17]]
```
difference / abs(matlab_value) * 100:
```text
[[1.3573683985e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.3573683985e-14]]
```

### K

MATLAB fixture:
```text
[[ 0.0352981035]
 [-0.1020555638]]
```
Python generated:
```text
[[ 0.0352981035]
 [-0.1020555638]]
```
Absolute difference |Python - MATLAB|:
```text
[[4.8572257327e-17]
 [8.3266726847e-17]]
```
difference / abs(matlab_value) * 100:
```text
[[1.3760585540e-13]
 [8.1589600521e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.3760585540e-13]
 [8.1589600521e-14]]
```

### Case c1 - stable1

### A

MATLAB fixture:
```text
[[-47.7101895784 -16.5077545489]
 [142.519386293   49.2983087269]]
```
Python generated:
```text
[[-47.7086537875 -16.5072238045]
 [142.5149433264  49.296772936 ]]
```
Absolute difference |Python - MATLAB|:
```text
[[0.0015357909 0.0005307444]
 [0.0044429666 0.0015357909]]
```
difference / abs(matlab_value) * 100:
```text
[[0.0032189998 0.0032151217]
 [0.0031174472 0.0031153014]]
```
difference / abs(python_value) * 100:
```text
[[0.0032191034 0.0032152251]
 [0.0031175444 0.0031153985]]
```

### B

MATLAB fixture:
```text
[[-3.5392912519e+10]
 [ 1.0330036018e+11]]
```
Python generated:
```text
[[-3.5391799362e+10]
 [ 1.0329713988e+11]]
```
Absolute difference |Python - MATLAB|:
```text
[[1113156.9878997803]
 [3220307.5004119873]]
```
difference / abs(matlab_value) * 100:
```text
[[0.003145141 ]
 [0.0031174214]]
```
difference / abs(python_value) * 100:
```text
[[0.0031452399]
 [0.0031175186]]
```

### C

MATLAB fixture:
```text
[[0.3903945854 0.1349529282]]
```
Python generated:
```text
[[0.3903945854 0.1349529284]]
```
Absolute difference |Python - MATLAB|:
```text
[[5.5511151231e-17 1.8879592334e-10]]
```
difference / abs(matlab_value) * 100:
```text
[[1.4219242097e-14 1.3989761163e-07]]
```
difference / abs(python_value) * 100:
```text
[[1.4219242097e-14 1.3989761144e-07]]
```

### D

MATLAB fixture:
```text
[[-0.0510830283]]
```
Python generated:
```text
[[-0.0510829816]]
```
Absolute difference |Python - MATLAB|:
```text
[[4.671740543e-08]]
```
difference / abs(matlab_value) * 100:
```text
[[9.1453868281e-05]]
```
difference / abs(python_value) * 100:
```text
[[9.1453951919e-05]]
```

### K

MATLAB fixture:
```text
[[-128.5923693697]
 [ 378.4428027305]]
```
Python generated:
```text
[[-128.5882912762]
 [ 378.4310049993]]
```
Absolute difference |Python - MATLAB|:
```text
[[0.0040780935]
 [0.0117977312]]
```
difference / abs(matlab_value) * 100:
```text
[[0.003171334]
 [0.003117441]]
```
difference / abs(python_value) * 100:
```text
[[0.0031714346]
 [0.0031175382]]
```

### Case c2 - base

### A

MATLAB fixture:
```text
[[ 0.7205837222  0.1060594787]
 [-0.0795111436  0.6450746993]]
```
Python generated:
```text
[[ 0.7205837222  0.1060594787]
 [-0.0795111436  0.6450746993]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.1102230246e-16 1.2073675393e-15]
 [5.5511151231e-17 1.5543122345e-15]]
```
difference / abs(matlab_value) * 100:
```text
[[1.5407273164e-14 1.1383872092e-12]
 [6.9815561321e-14 2.4095073582e-13]]
```
difference / abs(python_value) * 100:
```text
[[1.5407273164e-14 1.1383872092e-12]
 [6.9815561321e-14 2.4095073582e-13]]
```

### B

MATLAB fixture:
```text
[[0.2160625989]
 [0.0104204764]]
```
Python generated:
```text
[[0.2160625989]
 [0.0104204764]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.6653345369e-16]
 [1.7867651803e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[7.7076483653e-14]
 [1.7146674630e-12]]
```
difference / abs(python_value) * 100:
```text
[[7.7076483653e-14]
 [1.7146674630e-12]]
```

### C

MATLAB fixture:
```text
[[-0.5612280861 -0.2005688243]]
```
Python generated:
```text
[[-0.5612280861 -0.2005688243]]
```
Absolute difference |Python - MATLAB|:
```text
[[0.000000000e+00 5.273559367e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[0.0000000000e+00 2.6293016298e-13]]
```
difference / abs(python_value) * 100:
```text
[[0.0000000000e+00 2.6293016298e-13]]
```

### D

MATLAB fixture:
```text
[[0.0341709447]]
```
Python generated:
```text
[[0.0341709447]]
```
Absolute difference |Python - MATLAB|:
```text
[[3.469446952e-17]]
```
difference / abs(matlab_value) * 100:
```text
[[1.01532076e-13]]
```
difference / abs(python_value) * 100:
```text
[[1.01532076e-13]]
```

### K

MATLAB fixture:
```text
[[-0.1191957245]
 [-0.0998241745]]
```
Python generated:
```text
[[-0.1191957245]
 [-0.0998241745]]
```
Absolute difference |Python - MATLAB|:
```text
[[4.1633363423e-17]
 [2.0816681712e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[3.4928571150e-14]
 [2.0853347212e-13]]
```
difference / abs(python_value) * 100:
```text
[[3.4928571150e-14]
 [2.0853347212e-13]]
```

### Case c2 - stable1

### A

MATLAB fixture:
```text
[[-0.5925843083 -1.6575157395]
 [ 1.1677973019  2.1807032105]]
```
Python generated:
```text
[[-0.5925840562 -1.6575152993]
 [ 1.1677971903  2.1807029585]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.5209479904e-07 4.4015962097e-07]
 [1.1164223856e-07 2.5205103160e-07]]
```
difference / abs(matlab_value) * 100:
```text
[[4.2541592061e-05 2.6555381074e-05]
 [9.5600699182e-06 1.1558245541e-05]]
```
difference / abs(python_value) * 100:
```text
[[4.2541610159e-05 2.6555388126e-05]
 [9.5600708322e-06 1.1558246877e-05]]
```

### B

MATLAB fixture:
```text
[[-9.1023324376e+08]
 [ 6.2068064114e+08]]
```
Python generated:
```text
[[-9.1023310740e+08]
 [ 6.2068058018e+08]]
```
Absolute difference |Python - MATLAB|:
```text
[[136.3624964952]
 [ 60.956923604 ]]
```
difference / abs(matlab_value) * 100:
```text
[[1.4981049904e-05]
 [9.8209803181e-06]]
```
difference / abs(python_value) * 100:
```text
[[1.4981052149e-05]
 [9.8209812826e-06]]
```

### C

MATLAB fixture:
```text
[[0.2612281596 0.4807120673]]
```
Python generated:
```text
[[0.2612281596 0.4807120569]]
```
Absolute difference |Python - MATLAB|:
```text
[[5.5511151231e-17 1.0422709973e-08]]
```
difference / abs(matlab_value) * 100:
```text
[[2.1250064053e-14 2.1681814710e-06]]
```
difference / abs(python_value) * 100:
```text
[[2.1250064053e-14 2.1681815180e-06]]
```

### D

MATLAB fixture:
```text
[[-0.0449701548]]
```
Python generated:
```text
[[-0.0449701074]]
```
Absolute difference |Python - MATLAB|:
```text
[[4.7339732891e-08]]
```
difference / abs(matlab_value) * 100:
```text
[[0.0001052692]]
```
difference / abs(python_value) * 100:
```text
[[0.0001052693]]
```

### K

MATLAB fixture:
```text
[[-5.1967247201]
 [ 4.6342302524]]
```
Python generated:
```text
[[-5.1967237197]
 [ 4.6342298093]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.0003754607e-06]
 [4.4311014147e-07]]
```
difference / abs(matlab_value) * 100:
```text
[[1.9250114535e-05]
 [9.5616772868e-06]]
```
difference / abs(python_value) * 100:
```text
[[1.9250118241e-05]
 [9.5616782011e-06]]
```

### Case c3 - base

### A

MATLAB fixture:
```text
[[ 0.719961875   0.1003150382]
 [-0.079959425   0.6396647164]]
```
Python generated:
```text
[[ 0.719961875   0.1003150382]
 [-0.079959425   0.6396647164]]
```
Absolute difference |Python - MATLAB|:
```text
[[7.7715611724e-16 1.6930901126e-15]
 [3.7470027081e-16 4.4408920985e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[1.0794406541e-13 1.6877729822e-12]
 [4.6861301347e-13 6.9425309619e-14]]
```
difference / abs(python_value) * 100:
```text
[[1.0794406541e-13 1.6877729822e-12]
 [4.6861301347e-13 6.9425309619e-14]]
```

### B

MATLAB fixture:
```text
[[0.1298629452]
 [0.0151935747]]
```
Python generated:
```text
[[0.1298629452]
 [0.0151935747]]
```
Absolute difference |Python - MATLAB|:
```text
[[8.3266726847e-17]
 [1.4571677198e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[6.4118926837e-14]
 [9.5906839003e-13]]
```
difference / abs(python_value) * 100:
```text
[[6.4118926837e-14]
 [9.5906839003e-13]]
```

### C

MATLAB fixture:
```text
[[-0.9224874197  0.2459321951]]
```
Python generated:
```text
[[-0.9224874197  0.2459321951]]
```
Absolute difference |Python - MATLAB|:
```text
[[7.7715611724e-16 1.1102230246e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[8.4245714427e-14 4.5143460142e-14]]
```
difference / abs(python_value) * 100:
```text
[[8.4245714427e-14 4.5143460142e-14]]
```

### D

MATLAB fixture:
```text
[[-0.0151401229]]
```
Python generated:
```text
[[-0.0151401229]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.0234868508e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[6.7600960629e-13]]
```
difference / abs(python_value) * 100:
```text
[[6.7600960629e-13]]
```

### K

MATLAB fixture:
```text
[[-0.0303315513]
 [ 0.0322807574]]
```
Python generated:
```text
[[-0.0303315513]
 [ 0.0322807574]]
```
Absolute difference |Python - MATLAB|:
```text
[[4.8572257327e-17]
 [1.1796119637e-16]]
```
difference / abs(matlab_value) * 100:
```text
[[1.6013772848e-13]
 [3.6542264183e-13]]
```
difference / abs(python_value) * 100:
```text
[[1.6013772848e-13]
 [3.6542264183e-13]]
```

### Case c3 - stable1

### A

MATLAB fixture:
```text
[[  8.5074900183   2.2771537396]
 [-26.1334444463  -6.9193708716]]
```
Python generated:
```text
[[  8.5074900643   2.2771537512]
 [-26.1334446243  -6.9193709176]]
```
Absolute difference |Python - MATLAB|:
```text
[[4.5930903525e-08 1.1596145821e-08]
 [1.7808292441e-07 4.5930866222e-08]]
```
difference / abs(matlab_value) * 100:
```text
[[5.3988783326e-07 5.0923859992e-07]
 [6.8143686445e-07 6.6380119051e-07]]
```
difference / abs(python_value) * 100:
```text
[[5.3988783035e-07 5.0923859732e-07]
 [6.8143685980e-07 6.6380118610e-07]]
```

### B

MATLAB fixture:
```text
[[-4.1991779088e+08]
 [ 1.4854704687e+09]]
```
Python generated:
```text
[[-4.1991779349e+08]
 [ 1.4854704788e+09]]
```
Absolute difference |Python - MATLAB|:
```text
[[ 2.6111449599]
 [10.123790741 ]]
```
difference / abs(matlab_value) * 100:
```text
[[6.2182289406e-07]
 [6.8152083493e-07]]
```
difference / abs(python_value) * 100:
```text
[[6.2182289020e-07]
 [6.8152083029e-07]]
```

### C

MATLAB fixture:
```text
[[0.1796628693 0.0477875537]]
```
Python generated:
```text
[[0.1796628693 0.0477875537]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.1102230246e-16 9.8753713540e-12]]
```
difference / abs(matlab_value) * 100:
```text
[[6.1794795393e-14 2.0665153544e-08]]
```
difference / abs(python_value) * 100:
```text
[[6.1794795393e-14 2.0665153548e-08]]
```

### D

MATLAB fixture:
```text
[[-0.0170457019]]
```
Python generated:
```text
[[-0.0170457029]]
```
Absolute difference |Python - MATLAB|:
```text
[[1.0781461834e-09]]
```
difference / abs(matlab_value) * 100:
```text
[[6.3250325078e-06]]
```
difference / abs(python_value) * 100:
```text
[[6.3250321077e-06]]
```

### K

MATLAB fixture:
```text
[[  44.9509487392]
 [-150.788567617 ]]
```
Python generated:
```text
[[  44.9509490043]
 [-150.7885686445]]
```
Absolute difference |Python - MATLAB|:
```text
[[2.6506282325e-07]
 [1.0274276008e-06]]
```
difference / abs(matlab_value) * 100:
```text
[[5.8967125429e-07]
 [6.8136969335e-07]]
```
difference / abs(python_value) * 100:
```text
[[5.8967125081e-07]
 [6.8136968870e-07]]
```

