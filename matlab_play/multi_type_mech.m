
% This code include multiple types in the mechanical matching model

clear
global alp

%Careful with gamB,S>1, generate non-monotonity pdf at the tail, prediction sensitive to N
gamB=0.8;
gamS=0.8;

% Matching and separating technology
alp=5;  delta=2.2;

% Maximum number of edges to solve numerically
N=301;
% Mass of sellers relative to buyers
barMS=1;

% Specify the type specific visibility
Nx=5;   %number of types
sigxB=[1 2 4 7 10];
sigxS=[1 2 4 7 10];

wt_x=[0.8 0.12 0.05 0.02 0.01];

% Parameter for smooth updating
wt=0.5;

% initial guess
% dist. of number of sellers per buyer for Buyers
MB=ones(N,Nx)./(N*Nx); MB_check=zeros(N,Nx);
% dist. of number of buyers per seller for Sellers
MS=ones(N,Nx)./(N*Nx); MS_check=zeros(N,Nx);

%start with iteration

%define visibility for each (N,type)
vB=repmat((1:1:N)'.^gamB,1,Nx).*repmat(sigxB,N,1);
vS=repmat((1:1:N)'.^gamS,1,Nx).*repmat(sigxS,N,1);

%define overall visibility
HB_new=sum(sum(vB.*MB));
HS_new=sum(sum(vS.*MS));

HB=0;
HS=0;

while abs(HB_new-HB)>1e-10||abs(HS_new-HS)>1e-10
[abs(HB_new-HB) abs(HS_new-HS)]

%HB=wt*HB_new+(1-wt)*HB;  HS=wt*HS_new+(1-wt)*HS;
HB=HB_new; HS=HS_new;

X=match(HB,HS);

lamB=zeros(N,Nx); lamS=zeros(N,Nx); MB=zeros(N,Nx); MS=zeros(N,Nx);
%solve the system of equations defining stationary dist
lamB(1,:)=sigxB*X/(delta*HB); lamS(1,:)=sigxS*X/(delta*HS); MB(1,:)=1; MS(1,:)=1;
for i=1:1:N-1
     for j=1:1:Nx
        MB(i,j)=0*(MB(i,j)<0)+(MB(i,j)>=0)*MB(i,j);
        MS(i,j)=0*(MS(i,j)<0)+(MS(i,j)>=0)*MS(i,j);
     end
  lamB(i+1,:)=sigxB./(delta*(i+1)).*((i+1)^gamB-(i)^gamB./lamB(i,:))*X/HB+i/(i+1);
  lamS(i+1,:)=sigxS./(delta*(i+1)).*((i+1)^gamS-(i)^gamS./lamS(i,:))*X/HS+i/(i+1); 
  MB(i+1,:)=lamB(i,:).*MB(i,:); 
  MS(i+1,:)=lamS(i,:).*MS(i,:);
end

%normalize for each type
MB=MB./repmat(sum(MB),N,1);
MS=MS./repmat(sum(MS),N,1);

%first construct intensity matrix for each type
QB=zeros(N,N,Nx);  QS=zeros(N,N,Nx); 
%terminal states
QB(1,2,:)=(0+1)^gamB*sigxB*X/HB; QB(1,1,:)=-QB(1,2,:);
QB(end,end-1,:)=delta*(N-1); QB(end,end,:)=-QB(end,end-1,:);

QS(1,2,:)=(0+1)^gamS*sigxS*X/HS; QS(1,1,:)=-QS(1,2,:);
QS(end,end-1,:)=delta*(N-1); QS(end,end,:)=-QS(end,end-1,:);

for i=2:1:N-1
  QB(i,i+1,:)=i^gamB*sigxB*X/HB;
  QB(i,i-1,:)=delta*(i-1);
  QB(i,i,:)=-QB(i,i+1,:)-QB(i,i-1,:);
  
  QS(i,i+1,:)=i^gamS*sigxS*X/HS;
  QS(i,i-1,:)=delta*(i-1);
  QS(i,i,:)=-QS(i,i+1,:)-QS(i,i-1,:);
end
%analytical solution of stationary dist. given Q
for x=1:1:Nx
MB_check(:,x)=(ones(1,N)/(QB(:,:,x)+ones(N,N)))';
MS_check(:,x)=(ones(1,N)/(QS(:,:,x)+ones(N,N)))';
end

HB_new=sum(sum(vB.*MB_check.*repmat(wt_x,N,1)));
HS_new=sum(sum(vS.*MS_check.*repmat(wt_x,N,1)))*barMS;

end

MB_all=sum(MB.*repmat(wt_x,N,1),2);
MB_plot=MB_all(2:end)./sum(1-MB_all(1));

%matrix exponential to get transition
wTB=zeros(N,N);
for x=1:1:Nx
    wTB=wTB+wt_x(x)*expm(QB(:,:,x));
end

%check power law dist.
Nb=300;
Pb=1-cumsum(MB_plot(1:Nb));
%Ps=1-cumsum(MS);
vecN=(1:1:Nb)';
plot(log(vecN(Pb>0)),log(Pb(Pb>0)),'ro')
disp('power law coefficient')
slope=(log(vecN(Pb>0))'*log(vecN(Pb>0)))\(log(vecN(Pb>0))'*log(Pb(Pb>0)))

%report comparable moments to data
tabMB=zeros(21,1); tabMB(1:20)=MB_plot(1:20); tabMB(end)=1-sum(MB_plot(1:20));


%calculate sum of unconditional prob
temp=sum(wTB(22:end,:).*repmat(MB_all(22:end),1,N),1)/sum(MB_all(22:end));
tabTB=zeros(22,22); tabTB(1:21,1:21)=wTB(1:21,1:21); 
tabTB(1:21,22)=sum(wTB(1:21,22:end),2); 
tabTB(22,1:21)=temp(1:21); tabTB(22,22)=sum(temp(22:end));

