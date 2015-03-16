% Analytic solution
syms mw ma cpw cpa hwa he hr qw qa wt0 wt1 wt2 at0 at1 at2 ate atr real
w1 = mw*cpw*(wt1-wt0) - hwa*(at1-wt1);
a1 = ma*cpa*(at1-at0) - hwa*(wt1-at1) - he*(ate-at1) - hr*(atr-at1);
w2 = mw*cpw*(wt2-wt1) - qw;
a2 = ma*cpa*(at2-at1) - qa;
sol = solve(w1,a1,w2,a2,wt1,at1,wt2,at2)
mw = 0.00005; ma = 0.005; cpw = 4.218; cpa = 1.005; he = 50; hr = 20; hwa = 10; 
qa = 0.008; qw = 0.003;
at0 = 20; wt0 = 13; atr = 22.5; ate = 25.0;
at1 = eval(sol.at1)
at2 = eval(sol.at2)
wt1 = eval(sol.wt1)
wt2 = eval(sol.wt2)
