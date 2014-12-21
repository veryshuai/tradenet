% This code introduces sources of heterogeneity for buyers
% modified December 2014 to include transition matrix

clear;

%Start by bounding state space - maximum number of connections
N=300;
Ns=1;   %relative seller to buyer ratio
Nx=5;   %number of types of buyers
wt_x=[0.8 0.12 0.05 0.02 0.01];

%%cost parameter of buyer search and seller search

%simple quatratic
cb0=0.2;  cb1=2;
cs0=0.2;  cs1=2;
%network effects
gamB= 1;
gamS= 1;

%profit function parameters for buyer (g) and seller-buyer pair (f)
g=.95;
profx=[1 5 10 20 30];  %heterogeneity in profitability of different types of buyers
f= 0;

%discounting rate and exogenous destruction rate
rho=0.1;
delta=2;

%match function parameters
alp=6;

%%%%%%%%%%%%%%%START TO ITERATE ON MATCHING RATE
%initial guess of equilibrium objects thetab, thetas
thetas_new=0.01; 
thetab_new=0.01;
wt_old=0.3; % dampening parameter for updating theta, [0,1]

thetas=0;  thetab=0;

while norm(thetas_new-thetas)>1e-4||norm(thetab_new-thetab)>1e-4
    
    thetas=wt_old*thetas+(1-wt_old)*thetas_new;  thetab=wt_old*thetab+(1-wt_old)*thetab_new;
    
    %solve buyers problem
    
    %define each type x of buyer value function with 0,1,.....,N sellers
    %value function is N+1 by Nx
    
    %define buyer profit \pi(n,x)=x*n^g
    profb=kron([0:1:N]'.^g, profx);
    Vb_new=profb;
    Vb=zeros(N+1,Nx);
    
    %buyer effort to create vacancy
    v=zeros(N+1,Nx);
    
    netB=repmat((1:1:N)'.^gamB,1,Nx);
    while norm(Vb-Vb_new)>1e-6
        Vb=Vb_new;
        
        %start with boundary condition
        
        %optimal search effort
        v(N+1,:)=0;     
        v(1:N,:)=netB.*(thetab*(Vb(2:N+1,:)-Vb(1:N,:))/(cb0*cb1)).^(1/(cb1-1));
        
        Vb_new(N+1,:)=1./(rho+N*delta)*(profb(N,:)+N*delta*Vb(N,:));
        Vb_new(1,:)=1./(rho+v(1,:)*thetab).*(0-cb0*v(1,:).^cb1./netB(1,:)+thetab*v(1,:).*Vb(2,:));
        
        %the case of 1,2,...N-1 sellers
        Vb_new(2:N,:)=1./(rho+repmat((1:1:N-1)',1,Nx)*delta+v(2:N,:)*thetab).*(profb(2:N,:)-cb0*(v(2:N,:)).^cb1./netB(2:N,:)+delta*repmat((1:1:N-1)',1,Nx).*Vb(1:N-1,:)+thetab*v(2:N,:).*Vb(3:N+1,:));
          
    end
    
    %solve intensity matrix for each type of buyers
    QB=zeros(N+1,N+1,Nx);
    Mb_check=zeros(N+1,Nx);
    for x=1:1:Nx
        QB(1,2,x)=v(1,x)*thetab; QB(1,1,x)=-QB(1,2,x); 
        QB(end,end-1,x)=delta*N; QB(end,end,x)=-QB(end,end-1,x);
        for i=2:1:N
            QB(i,i+1,x)=v(i,x)*thetab; QB(i,i-1,x)=delta*(i-1); QB(i,i,x)=-(QB(i,i+1,x)+QB(i,i-1,x));
        end
        Mb_check(:,x)=(ones(1,N+1)/(QB(:,:,x)+ones(N+1,N+1)))';
    end
      
    %solve buyer stationary dist. (using balancing)
    Mb=zeros(N+1,Nx);
    
    Mb(1,:)=1;   %normalize later
    Mb(2,:)=Mb(1,:).*v(1,:)*thetab/delta;
    %Mass of buyers with 2, 3, ...,N-1 sellers
    for i=3:1:N
        Mb(i,:)=1/((i-1)*delta)*(-v(i-2,:)*thetab.*Mb(i-2,:)+v(i-1,:)*thetab.*Mb(i-1,:)+(i-2)*delta*Mb(i-1,:));
      %  if Mb(i,j)<0  %if hit negative mass, exit
         for j=1:1:Nx
            Mb(i,j)=0*(Mb(i,j)<0)+(Mb(i,j)>=0)*Mb(i,j);
         end
    end
    Mb(N+1,:)=v(N,:)*thetab.*Mb(N,:)/(N*delta);
    Mb=Mb./repmat(sum(Mb),N+1,1);
    
    %solve the value of seller-buyer pair
    profs=kron([1:1:N]'.^f, profx);
    Vs_new=profs./rho;
    Vs=zeros(N,Nx);
    while norm(Vs-Vs_new)>1e-6
        Vs=Vs_new;
        
        %start with boundary condition
        Vs_new(1,:)=1./(rho+delta+v(2,:)*thetab).*(profs(1,:)+v(2,:)*thetab.*Vs(2,:));
        Vs_new(N,:)=1./(rho+delta*N).*(profs(N,:)+(N-1)*delta*Vs(N-1,:));
        Vs_new(2:N-1,:)=1./(rho+repmat((2:1:N-1)',1,Nx)*delta+v(3:N,:)*thetab).*(profs(2:N-1,:)+delta*repmat((1:1:N-2)',1,Nx).*Vs(1:N-2,:)+thetab*v(3:N,:).*Vs(3:N,:));
            
    end 
    EVs=sum(sum(Vs.*Mb(1:N,:).*repmat(wt_x,N,1)));
    netS=(1:1:N)'.^gamS;
    u=netS.*(EVs*thetas/(cs0*cs1)).^(1/(cs1-1));
    
    %solve intensity matrix for sellers
    QS=zeros(N+1,N+1);
        QS(1,2)=u(1)*thetas; QS(1,1)=-QS(1,2); 
        QS(end,end-1)=delta*N; QS(end,end)=-QS(end,end-1);
        for i=2:1:N
            QS(i,i+1)=u(i)*thetas; QS(i,i-1)=delta*(i-1); QS(i,i)=-(QS(i,i+1)+QB(i,i-1));
        end    
    Ms_check=(ones(1,N+1)/(QS+ones(N+1,N+1)))';
    
    %iterate to get seller size dist.
    Ms=zeros(N+1,1);
     
    Ms(1)=1;   %normalize later
    Ms(2)=Ms(1)*u(1)*thetas/delta;
    %Mass of sellers with 2, 3, ...,N-1 buyers
    for i=3:1:N
        Ms(i)=1/((i-1)*delta)*(-u(i-2)*thetas*Ms(i-2)+u(i-1)*thetas*Ms(i-1)+(i-2)*delta*Ms(i-1));
          if Ms(i)<0  %if hit negative mass, exit
             Ms(i)=0;
             break
         end
    end
    Ms(N+1)=u(N)*thetas*Ms(N)/(N*delta);
    Ms=Ms./sum(Ms);
    
    % %now aggregate up to V/U
    V=sum(sum(v.*Mb));        %total buyer search (vacancy)
    U=sum(u.*Ms(1:N))*Ns;   %total seller search 
    
    thetab_new=U/(U^alp+V^alp)^(1/alp);
    thetas_new=V/(U^alp+V^alp)^(1/alp);
    
    [norm(thetas_new-thetas) norm(thetab_new-thetab)]
end

%transition matrix

%matrix exponential to get transition
wTB=zeros(N+1,N+1);
for x=1:1:Nx
    wTB=wTB+wt_x(x)*expm(QB(:,:,x));
end

Mbs=sum(Mb.*repmat(wt_x,N+1,1),2);
Mbs_plot=Mbs(2:end)./sum(Mbs(2:end));

%check power law dist.
Ntr=300;
Pb=1-cumsum(Mbs_plot(1:Ntr));
vecN=(1:1:Ntr)';
plot(log(vecN(Pb>0)),log(Pb(Pb>0)),'ro')
disp('power law coefficient')
slope=(log(vecN(Pb>0))'*log(vecN(Pb>0)))\(log(vecN(Pb>0))'*log(Pb(Pb>0)))

%report comparable moments to data
tabMB=zeros(21,1); tabMB(1:20)=Mbs_plot(1:20); tabMB(end)=1-sum(Mbs_plot(1:20));

%calculate sum of unconditional prob
temp=sum(wTB(22:end,:).*repmat(Mbs(22:end),1,N+1),1)/sum(Mbs(22:end));
tabTB=zeros(22,22); tabTB(1:21,1:21)=wTB(1:21,1:21); 
tabTB(1:21,22)=sum(wTB(1:21,22:end),2); 
tabTB(22,1:21)=temp(1:21); tabTB(22,22)=sum(temp(22:end));
