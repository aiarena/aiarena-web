create database test_aiarena;
create user aiarena with encrypted password 'aiarena';
grant all privileges on database test_aiarena to aiarena;