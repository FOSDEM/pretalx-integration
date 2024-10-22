-- export devrooms for postfix virtual postmap file
with managers as
((select ts.mail, email FROM submission_track t
join devroom_settings_tracksettings ts on t.id=ts.track_id
join event_teaminvite et on et.team_id=ts.manager_team_id
where ts.track_type='D'
  and t.event_id=6
order by mail, email)
union all
(select ts.mail,  email FROM submission_track t
join devroom_settings_tracksettings ts on t.id=ts.track_id
join event_team_members em on em.team_id=ts.manager_team_id
join person_user u on em.user_id=u.id
where ts.track_type='D' and t.event_id=6
order by mail, email))
select mail||E'\t'||string_agg(email,',' order by email)||',devrooms@fosdem.org' from managers group by mail order by mail; 

