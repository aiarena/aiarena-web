delimiter $$
-- use `aiarena_beta`$$
drop procedure if exists `generate_round_robin`;
create procedure `generate_round_robin`(in round_id int(11)) 
begin 
  select count(*) 
  into   @map_count 
  from   core_map; 
   
  select count(*) 
  into   @active_bots_count 
  from   core_bot; 
   
  if @map_count > 0 
    then 
    if @active_bots_count >1 
      then 
      select max(id) 
      into   @max_map_id 
      from   core_map; 
       
      select min(id) 
      into   @min_map_id 
      from   core_map; 
       
      select max(id) 
      into   @max_round_id 
      from   core_round; 
       
      select max(id) 
      into   @max_match_id 
      from   core_match; 
      
      drop temporary table if exists active_bots_1;
      create temporary table active_bots_1
        select          a.id
                        from       core_bot a 
                        where        a.active = 1 ;
      
      drop temporary table if exists active_bots_2;
      create temporary table active_bots_2 like active_bots_1;

      insert into active_bots_2
      select * from active_bots_1;

           drop temporary table if exists active_bots_3;
      create temporary table active_bots_3 like active_bots_1;

      insert into active_bots_3
      select * from active_bots_1;
    
drop temporary table if exists active_bots_4;
create temporary table active_bots_4 like active_bots_1;


      insert into active_bots_4
      select * from active_bots_1;
create index idx_active_bots_1_id on active_bots_1(id);
create index idx_active_bots_2_id on active_bots_2(id);
create index idx_active_bots_3_id on active_bots_3(id);
create index idx_active_bots_4_id on active_bots_4(id);
drop temporary table if exists  core_round_robin_1; 
create temporary table  core_round_robin_1 (
  `id` int(11) not null auto_increment,
  `bot_id1` int(11) not null default '0',
  `bot_id2` int(11) not null default '0',
  `map_id` double(22,0) default null,
  primary key (`id`),
  unique key `id_unique` (`id`)
) engine=innodb auto_increment=512 default charset=utf8;

insert into core_round_robin_1(bot_id1,bot_id2,map_id)

      select bot_id1 , 
             bot_id2 , 
             round((rand() * (@max_map_id-@min_map_id))+@min_map_id) as map_id 
      from   ( 
                        select     a.id as bot_id1, 
                                   b.id as bot_id2 
                        from       active_bots_1 a
                        inner join active_bots_2 b
                        on         a.id <= b.id 
                        union 
                        select     b.id, 
                                   a.id 
                        from       active_bots_3 a
                        inner join active_bots_4 b
                        on         b.id < a.id 
                        order by   rand() ) bots; 
                        
      drop temporary table if exists  core_round_robin_2; 
      create temporary table core_round_robin_2 like core_round_robin_1;

      insert into core_round_robin_2
      select * from core_round_robin_1;
      select 1 
      into   @counter; 
       
      select max(id) 
      into   @max_round_robin 
      from   core_round_robin_1; 
     
      while @counter < @max_round_robin 
      do 
      select map_id 
      into   @map_id 
      from   core_round_robin_1
      where  id = @counter; 
       
      insert into core_match 
                  ( 
                              created, 
                              map_id, 
                              round_id 
                  ) 
                  values 
                  ( 
                              now(), 
                              @map_id, 
                              round_id 
                  ); 
       
      select last_insert_id() 
      into   @match_id; 
       
      insert into core_participation
                  ( 
                              participant_number, 
                              bot_id, 
                              match_id 
                  ) 
      select participant_number, 
             bot_id, 
             @match_id 
      from   ( 
                    select 
                           1   as participant_number, 
                           bot_id1 as bot_id 
                    from   core_round_robin_1
                    union all 
                    select   
                             2, 
                             bot_id2 
                    from     core_round_robin_2
                    order by id, 
                             2) k 
      where  k.id = @counter ; 
       
      set @counter = @counter +1; 
    end while; 
  end if;
end if; 
end$$

delimiter ;
