function blurreador(imagen);
% Este programa toma una imagen .jpg y la blurrea (pone borrosa).
%%
a=imread(imagen); %Cambiar original por el nombre del archivo a blurrear
a=double(a);

size=15;  %Define el entorno de puntos  de cada pixel que toma para blurrear.
b=ones(size,size);b=b/sum(sum(b));
%%

z=min(a,[],3);
z1=(z>mean(mean(z)));
z1=double(z1);
z1=255*z1;
z2=conv2(z1,b,'same');
imagesc(z2);
z3=uint8(zeros(864,1152,3));

for i=1:3
    z3(:,:,i)=uint8(round(z2));
end

imwrite(z3,'blur.jpg','jpeg'); %cambiar blur por el nombre de archivo de salida que querramos.