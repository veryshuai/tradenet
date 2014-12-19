
% Define the matching function

function out=match(HB,HS)
global alp
 %1. matching function (1)
 out=HB*HS/((HB^alp+HS^alp)^(1/alp));

 %  matching function (2)
 % out=HB^alp*HS^(1-alp);

end