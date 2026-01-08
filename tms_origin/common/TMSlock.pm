package TMSlock;

###################################################################################################
#
# TMSlock.pm
#
###################################################################################################

use strict;

use TMSstr;
use TMScommon;

###################################################################################################

sub data_updating_page
{
  my ( $other_ip ) = @_;

  my $lang = &TMSstr::get_lang();

  my $str_DATA_IS_UNDER_UPDATING  = &TMSstr::get_str( "DATA_IS_UNDER_UPDATING" );
  my $str_TRY_AGAIN_AFTER_A_WHILE = &TMSstr::get_str( "TRY_AGAIN_AFTER_A_WHILE" );
  my $str_USING_USER              = &TMSstr::get_str( "USING_USER" );
  my $str_LOCAL_USER              = &TMSstr::get_str( "LOCAL_USER" );
  my $str_REMOTE_USER             = &TMSstr::get_str( "REMOTE_USER" );
  my $str_BACK                    = &TMSstr::get_str( "BACK" );

  my $title = $str_DATA_IS_UNDER_UPDATING;

  my $tbl_width = 630;
  my $menu_color = '#ED1C24';
  my $body_color = '#FDE1D4';

  my $other_user;
  if( $other_ip eq '127.0.0.1' ){ $other_user = $str_LOCAL_USER; }
  else{ $other_user = "$str_REMOTE_USER ( $other_ip )"; }

  my $html = 	"<html lang=$lang>\n".
		"<head>\n".
		&TMScommon::meta_content_type( $lang ).
		&TMScommon::meta_no_cache_tag().
		"<title>$title</title>\n".
		"</head>\n".
		"<body bgcolor=#C7C4E2><center>\n".
		&TMScommon::make_header('menu','dummy', $lang)."<BR>".

		"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
		"<tr align=center bgcolor=$menu_color>\n".
		"<th><font size=+2 color=white>$title</font></th>\n".
		"</tr>\n".
		"<tr align=center bgcolor=$body_color><td>\n".
		"<BR><BR><BR>\n".
		"<font size=+1><B>\n".
		"$str_DATA_IS_UNDER_UPDATING<BR>\n".
		"$str_TRY_AGAIN_AFTER_A_WHILE<BR>\n".
		"</B></font>\n".
		"<BR><BR>\n".
		"<font size=+1><B>$str_USING_USER : </B></font>\n".
		"<font size=+1 color=blue><B>$other_user</B></font><BR>\n".
		"<BR><BR>\n".
		"<A HREF=\"javascript:history.back()\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
		"<BR><BR><BR><BR>\n".
		"</td></tr>\n".
		"</table><BR>\n".

		&TMScommon::make_footer('dummy','menu', $lang).
		"</center></body></html>\n";
  return $html;
}

###################################################################################################

sub operation_lock_page
{
  my ( $other_ip ) = @_;

  my $lang = &TMSstr::get_lang();

  my $str_DATA_IS_UNDER_UPDATING  = &TMSstr::get_str( "DATA_IS_UNDER_UPDATING" );
  my $str_BE_IN_USE_BY_OTHER_USER = &TMSstr::get_str( "BE_IN_USE_BY_OTHER_USER"	);
  my $str_TRY_AGAIN_AFTER_A_WHILE = &TMSstr::get_str( "TRY_AGAIN_AFTER_A_WHILE" );
  my $str_USING_USER              = &TMSstr::get_str( "USING_USER" );
  my $str_LOCAL_USER              = &TMSstr::get_str( "LOCAL_USER" );
  my $str_REMOTE_USER             = &TMSstr::get_str( "REMOTE_USER" );
  my $str_BACK                    = &TMSstr::get_str( "BACK" );

  my $title = $str_DATA_IS_UNDER_UPDATING;

  my $tbl_width = 630;
  my $menu_color = '#ED1C24';
  my $body_color = '#FDE1D4';

  my $other_user;
  if( $other_ip eq '127.0.0.1' ){ $other_user = $str_LOCAL_USER; }
  else{ $other_user = "$str_REMOTE_USER ( $other_ip )"; }

  my $html = 	"<html lang=$lang>\n".
		"<head>\n".
		&TMScommon::meta_content_type( $lang ).
		&TMScommon::meta_no_cache_tag().
		"<title>$title</title>\n".
		"</head>\n".
		"<body bgcolor=#C7C4E2><center>\n".
		&TMScommon::make_header('menu','dummy', $lang)."<BR>".

		"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
		"<tr align=center bgcolor=$menu_color>\n".
		"<th><font size=+2 color=white>$title</font></th>\n".
		"</tr>\n".
		"<tr align=center bgcolor=$body_color><td>\n".
		"<BR><BR><BR>\n".
		"<font size=+1><B>\n".
		"$str_BE_IN_USE_BY_OTHER_USER<BR>\n".
		"$str_TRY_AGAIN_AFTER_A_WHILE<BR>\n".
		"</B></font>\n".
		"<BR><BR>\n".
		"<font size=+1><B>$str_USING_USER : </B></font>\n".
		"<font size=+1 color=blue><B>$other_user</B></font><BR>\n".
		"<BR><BR>\n".
		"<A HREF=\"javascript:history.back()\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
		"<BR><BR><BR><BR>\n".
		"</td></tr>\n".
		"</table><BR>\n".

		&TMScommon::make_footer('dummy','menu', $lang).
		"</center></body></html>\n";
  return $html;
}

###################################################################################################

sub create_lockfile
{
  my ($lockfile, $ip, $level, $timeout, $r_other) = @_;

  if( &check_lockfile($lockfile,$ip,$r_other) ){	# ロックファイルをチェック
    return 1;
  }

  &update_lockfile($lockfile,$ip,$level,$timeout);	# ロックファイルを作る
  return 0;
}

###################################################################################################

sub check_lockfile
{
  my ($lockfile, $ip, $r_other) = @_;

  if( -f $lockfile ){
    if( open(LOCK,"< $lockfile") ){

      my $l_ip      = "";
      my $l_level   = "";
      my $l_timeout = "";

      while(<LOCK>){
        $_ =~ s/\n$//;
        if( m/^ip (.+)/      ){ $l_ip      = $1; }
        if( m/^level (.+)/   ){ $l_level   = $1; }
        if( m/^timeout (.+)/ ){ $l_timeout = $1; }
      }
      close(LOCK);

      my $now = time();		# 現在時刻

      # ロックファイルの値があるか？
      if( (length($l_ip) == 0) || (length($l_level) == 0)
          || (length($l_timeout) == 0) ){ unlink($lockfile); }

      # レベル１でなく、同じＩＰなら無視
      elsif( ($l_ip eq $ip) && ($l_level != 1) ){ unlink($lockfile); }

      # タイムアウトしている、タイムアウトが15分以上未来の場合は削除
      elsif( ($l_timeout < $now) || ($l_timeout > ($now + 900)) ){ unlink($lockfile); }

      else{ $$r_other = $l_ip; return 1; }	# 使用しているユーザーのＩＰを返す
    }
  }
  return 0;
}

###################################################################################################

sub update_lockfile
{
  my ($lockfile, $ip, $level, $timeout) = @_;

  my $now = time();	# 現在時刻
  $timeout += $now;

  if( open(LOCK,"> $lockfile") ){
    print LOCK	"ip $ip\n".
		"level $level\n".
		"timeout $timeout\n";
    close(LOCK);
  }

}

###################################################################################################
1;
