syms ca cw hwin hwa

A0 = diag([cw,ca]);
A1 = [hwa, -hwa; -hwa, hwa+hwin];
Z = zeros(2,2);
Z2 = zeros(4,4);
B0 = [ A0+A1, Z; -A0, A0];
B1 = [Z,-A0; Z Z];
n = 3;
An = [B0 zeros(4,4*(n-1));
    zeros(4*(n-1),4*(n))];
for i = 1:(n-1)
    An((i*4+1):(i+1)*4,(i*4+1):(i+1)*4) = B0;
    An((i*4+1):(i+1)*4,((i-1)*4+1):i*4) = B1;
end
% invB0 = inv(B0);
% C = B1*invB0;
invA01 = inv(A0+A1);
A0invA01 = A0*invA01;
invB0 = [invA01, Z; invA01, inv(A0)];
C =  [-A0*invA01, -eye(2); Z Z];
invB0C = [-invA01*A0*invA01, -invA01;
    -invA01*A0*invA01, -invA01];
invAn = [invB0 zeros(4,4*(n-1));
    zeros(4*(n-1),4*(n))];
for j = 1:n
    for i = 1:(n+1-j)
        ind = ((i-1)*4+1):i*4;
        invAn(ind+4*(j-1),ind) = (-1)^(j-2)*invB0*C^(j-1);
        
    end 
end
si = sym('s',[n 1]);
s = [0,0,si(1),0];
for i = 2:n
 s = [s,0,0,si(i),0];
end
S = diag(s);
Sx = invAn*S*transpose(invAn)