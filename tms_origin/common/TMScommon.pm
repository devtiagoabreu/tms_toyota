package TMScommon;

###################################################################################################
#
# TMScommon.pm
#
###################################################################################################

use strict;
use DirHandle;
use Win32;
use Cwd;

use TMSstr;

###################################################################################################

sub log_entry	# ログファイルに書き込む
{
  my ($message) = @_;

  my $log_file = '../check/tms.log';	# 拡張子 .log を変えちゃダメ！！

  ## ログファイルのローテーション ##
  if( -f $log_file ){
    my @filestat = stat $log_file;
    my $logsize = $filestat[7];
    if( $logsize >= (50*1024) ){  # 50KB

      my $dst = $log_file; $dst =~ s/\.log$/3.log/;
      my $src = $log_file; $src =~ s/\.log$/2.log/;
      if( -f $dst  ){ unlink( $dst ); }
      if( -f $src  ){ rename( $src, $dst ); }

      $dst = $src;
      $src = $log_file; $src =~ s/\.log$/1.log/;
      if( -f $src  ){ rename( $src, $dst ); }

      $dst = $src;
      $src = $log_file;
      rename( $src, $dst );
    }
  }

  ## ログデータの書き込み ##

  my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);  # 現在日時
  my $day_time = sprintf("%02d/%02d/%02d %02d:%02d:%02d",($year+1900),($mon+1),$mday,$hour,$min,$sec);

  if( open(FILE,">> $log_file") ){
    
    print FILE "[$day_time $ENV{REMOTE_ADDR}] $message\n";
    close(FILE);
  }

}

###################################################################################################

sub make_dir
{
  my($dname) = @_;

  if( -d $dname ){ return; }
  if( -f $dname ){ unlink $dname; }
  mkdir $dname;
}

################################################################################
# リストに重複しないで登録

sub entry_to_list
{
  my ($r_list, $val) = @_;

  for( my $i=0; $i<=$#$r_list; $i++ ){
    if( $$r_list[$i] eq $val ){ return $i; }
  }
  push(@$r_list,$val);
  return $#$r_list;
}

###################################################################################################
# リストから削除

sub delete_from_list
{
  my ($r_list, $item) = @_;

  my $count = 0;
  for( my $i=$#$r_list; $i>=0; $i-- ){
    if( $$r_list[$i] eq $item ){
      splice( @$r_list, $i, 1 );
      ++$count;
    }
  }

  return $count;
}

###################################################################################################

sub get_shift_id
{
 return ( 'A','B','C','D','E' );
}

sub shiftnum_to_shiftname
{
  my ($shift_num) = @_;

  my @shift_id = &get_shift_id();

  my @s = split(/\./,$shift_num);
  my $shift_name = "$s[0]/$s[1]/$s[2].$shift_id[$s[3]]";

  return $shift_name;
}

sub daynum_to_dayname
{
  my ($day_num) = @_;

  my @s = split(/\./,$day_num);
  my $day_name = "$s[0]/$s[1]/$s[2]";

  return $day_name;
}

###################################################################################################

sub get_old_ym
{
  my ( $ym, $num ) = @_;

  my $y = int( $ym / 100 );  # yyyymm/100 -> 整数部 -> yyyy
  my $m = int( $ym % 100 );  # yyyymm/100 -> 余り -> mm

  $m = ($m - $num);			# $numヶ月前の日付
  while( $m < 1 ){ $y -= 1; $m += 12; }	# 月が1未満なら年を1減らして月を12増やす
  my $old_ym = (($y * 100) + $m);	# yyyymmの形に戻す

  return $old_ym;
}

#---------------------------------------------------------------------------

sub get_ym_by_dot
{
  my( $day ) = @_;

  my @d = split(/\./,$day);		# $day = 2004.10.12.1
  my $ym = (($d[0] *100) + $d[1]);	# $ym  = 200410
  return $ym;
}

# -------------------------------------------------------------------------------

sub get_ym_by_space
{
  my( $day ) = @_;

  my @d = split(/ /,$day);		# $day = "2004 11 2 2 18 54 41"
  my $ym = (($d[0] *100) + $d[1]);	# $ym  = "200411"
  return $ym;
}

###################################################################################################

# 期間の条件にマッチするファイル抽出

# (入) $period	→ 期間の種類
# (入) @shift	→ シフト、日付、月（内部形式：2003.01.02.0）

# (出) @file	← ファイル名（フルパス）
# (出) @index	← 対応する期間名の表示用文字列（2003/01/02.A）

sub get_shift_file_list
{
  my ($period, $r_shift, $r_file, $r_index) = @_;

  my @shift_id = &get_shift_id();	# 'A','B','C','D','E'

  my $dname;
  if(    $period eq "shift" ){ $dname = "..\\..\\tmsdata\\shift-shift"; }
  elsif( $period eq "date"  ){ $dname = "..\\..\\tmsdata\\shift-date";  }
  elsif( $period eq "week"  ){ $dname = "..\\..\\tmsdata\\shift-week";  }
  elsif( $period eq "month" ){ $dname = "..\\..\\tmsdata\\shift-month"; }

  my $dir = new DirHandle $dname;	# ディレクトリのファイルリストを取得する
  my @dirs = $dir->read;		# dirの結果を配列に入れる
  $dir->close;
  @dirs = sort @dirs;		# 配列をソートする。

  foreach my $f ( @dirs ){
    foreach( @$r_shift ){
      my $mstr = $_;		# foreach で読み出した変数を直接変更してはダメ！！
      $mstr =~ s/\./\\./g;	# シフト名の . をエスケープする。
      if( $f =~ m/^$mstr\.txt$/ ){

        push(@$r_file,"$dname\\$f");

        my @d = split(/\./,$f);
        my $index;
        if(    $period eq "shift" ){ $index = "$d[0]/$d[1]/$d[2].$shift_id[$d[3]]"; }
        elsif( $period eq "date"  ){ $index = "$d[0]/$d[1]/$d[2]"; }
        elsif( $period eq "week"  ){ $index = "$d[0]/$d[1]/$d[2]"; }
        elsif( $period eq "month" ){ $index = "$d[0]/$d[1]"; }
        push(@$r_index,$index);

        last;
      }
    }
  }

}

sub get_operator_file_list
{
  my ($period, $r_day, $r_file, $r_index) = @_;

  my $dname;
  if(    $period eq "date"  ){ $dname = "..\\..\\tmsdata\\operator-date";  }
  elsif( $period eq "week"  ){ $dname = "..\\..\\tmsdata\\operator-week";  }
  elsif( $period eq "month" ){ $dname = "..\\..\\tmsdata\\operator-month"; }

  my $dir = new DirHandle $dname;	# ディレクトリのファイルリストを取得する
  my @dirs = $dir->read;		# dirの結果を配列に入れる
  $dir->close;
  @dirs = sort @dirs;		# 配列をソートする。

  foreach my $f ( @dirs ){
    foreach( @$r_day ){
      my $mstr = $_;		# foreach で読み出した変数を直接変更してはダメ！！
      $mstr =~ s/\./\\./g;	# 日付の . をエスケープする。
      if( $f =~ m/^$mstr\.txt$/ ){

        push(@$r_file,"$dname\\$f");

        my @d = split(/\./,$f);
        my $index;
        if(    $period eq "date"  ){ $index = "$d[0]/$d[1]/$d[2]"; }
        elsif( $period eq "week"  ){ $index = "$d[0]/$d[1]/$d[2]"; }
        elsif( $period eq "month" ){ $index = "$d[0]/$d[1]"; }
        push(@$r_index,$index);

        last;
      }
    }
  }
}

###################################################################################################

sub get_now_date
{
  my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
  my $now_date = sprintf("%04d/%02d/%02d %02d:%02d",($year+1900),($mon+1),$mday,$hour,$min);
  return $now_date;
}

###################################################################################################

sub get_detail_stop_jat
{
  my ($r_all, $r_stop, $r_wf1, $r_wf2, $r_lh) = @_;

  my @stop = ();
  $stop[ 0] = $$r_all[17];	# Warp top miss
  $stop[ 1] = $$r_all[ 0];	# Warp miss
  $stop[ 2] = $$r_all[ 1];	# False selvage miss / CC Front
  $stop[ 3] = $$r_all[ 3];	# leno(L) miss
  $stop[ 4] = $$r_all[ 2];	# Leno(R) miss

  $stop[ 5] = 0;		# Weft
  for( my $i=5;  $i<=16; $i++ ){ $stop[ 5] += $$r_all[$i]; }
  for( my $i=18; $i<=23; $i++ ){ $stop[ 5] += $$r_all[$i]; }

  $stop[ 6] = $$r_all[24];	# Warp out
  $stop[ 7] = $$r_all[25];	# Cloth doffing
  $stop[ 8] = $$r_all[ 4];	# Manual stop
  $stop[ 9] = $$r_all[39];	# Power off

  $stop[10] = 0;		# Other
  for( my $i=26; $i<=38; $i++ ){ $stop[10] += $$r_all[$i]; }

  $stop[11] = 0;		# CC Back

  my @wf1  = ();
  for( my $i=0; $i<6; $i++ ){ $wf1[$i] = $$r_all[$i+5]; }

  my @wf2 = ();
  for( my $i=0; $i<6; $i++ ){ $wf2[$i] = $$r_all[$i+11]; }

  my @lh = ();
  for( my $i=0; $i<6; $i++ ){ $lh[$i] = $$r_all[$i+18]; }

  @$r_stop = @stop;
  @$r_wf1  = @wf1;
  @$r_wf2  = @wf2;
  @$r_lh   = @lh;
}

#--------------------------------------------------------------

sub get_detail_stop_lwt
{
  my ($r_all, $r_stop, $r_wf1, $r_wf2, $r_lh) = @_;

  my @stop = ();
  $stop[ 0] = $$r_all[10];	# Warp top miss
  $stop[ 1] = $$r_all[ 0];	# Warp miss
  $stop[ 2] = $$r_all[ 1];	# False selvage miss / CC Front
  $stop[ 3] = $$r_all[ 4];	# leno(L) miss
  $stop[ 4] = $$r_all[ 3];	# Leno(R) miss

  $stop[ 5] = 0;		# Weft
  for( my $i=6;  $i<=9;  $i++ ){ $stop[ 5] += $$r_all[$i]; }  # WF1
  for( my $i=11; $i<=14; $i++ ){ $stop[ 5] += $$r_all[$i]; }  # LH
  for( my $i=20; $i<=23; $i++ ){ $stop[ 5] += $$r_all[$i]; }  # WF2

  $stop[ 6] = $$r_all[15];	# Warp out
  $stop[ 7] = $$r_all[16];	# Cloth doffing
  $stop[ 8] = $$r_all[ 5];	# Manual stop
  $stop[ 9] = $$r_all[30];	# Power off

  $stop[10] = 0;		# Other
  for( my $i=17; $i<=19; $i++ ){ $stop[10] += $$r_all[$i]; }
  for( my $i=24; $i<=29; $i++ ){ $stop[10] += $$r_all[$i]; }

  $stop[11] = $$r_all[ 2];	# CC Back

  my @wf1 = (0,0,0,0,0,0);  # ４色分しかデータはないが、ＴＭＳ内部は６色分持つ
  for( my $i=0; $i<4; $i++ ){ $wf1[$i] = $$r_all[$i+6]; }

  my @wf2 = (0,0,0,0,0,0);  # ４色分しかデータはないが、ＴＭＳ内部は６色分持つ
  for( my $i=0; $i<4; $i++ ){ $wf2[$i] = $$r_all[$i+20]; }

  my @lh = (0,0,0,0,0,0);  # ４色分しかデータはないが、ＴＭＳ内部は６色分持つ
  for( my $i=0; $i<4; $i++ ){ $lh[$i] = $$r_all[$i+11]; }

  @$r_stop = @stop;
  @$r_wf1  = @wf1;
  @$r_wf2  = @wf2;
  @$r_lh   = @lh;
}

###################################################################################################

sub meta_content_type
{
  my( $lang ) = @_;

  my $charset;
  if(    $lang eq 'zh-cn' ){ $charset = 'gb2312';     }
  elsif( $lang eq 'zh-tw' ){ $charset = 'big5';       }
  elsif( $lang eq 'ko'    ){ $charset = 'euc-kr';     }
  elsif( $lang eq 'ja'    ){ $charset = 'Shift_JIS';  }
  elsif( $lang eq 'pt'    ){ $charset = 'ISO-8859-1'; }
  else{                      $charset = 'ISO-8859-1'; }  # デフォルト("en")

  return	"<meta http-equiv=\"Content-Type\" content=\"text/html; charset=$charset\">\n";
}

###################################################################################################

sub meta_no_cache_tag
{
  return	"<meta http-equiv=\"cache-control\" content=\"no-cache\">\n".
		"<meta http-equiv=\"pragma\" content=\"no-cache\">\n".
		"<meta http-equiv=\"expires\" content=\"0\">\n";
}

###################################################################################################

sub make_header
{
  my @arg = @_;
  my $lang = $arg[2];

  my $str_MENU    = &TMSstr::get_str( "MENU"	);
  my $str_SUBMENU = &TMSstr::get_str( "SUBMENU"	);
  #my $str_BACK    = &TMSstr::get_str( "BACK"	);

  my @button = ();

  my $image_path = 'image';
  unless( -d $image_path ){ $image_path = '../image'; }

  for( my $i=0; $i<=1; $i++ ){
    if( $arg[$i] eq "menu" ){
      $button[$i] =	"<a href=\"../\"><IMG SRC=\"$image_path/menu_$lang.jpg\" width=78 height=30 alt=\"$str_MENU\" border=0></a>".
			"<IMG src=\"$image_path/space.jpg\" width=2 height=30>";
    }
    elsif( $arg[$i] eq "submenu" ){
      $button[$i] =	"<a href=\"./\"><IMG SRC=\"$image_path/submenu_$lang.jpg\" width=78 height=30 alt=\"$str_SUBMENU\" border=0></a>".
			"<IMG src=\"$image_path/space.jpg\" width=2 height=30>";
    }
#   elsif( $arg[$i] eq "back" ){
#     $button[$i] =	"<a href=\"../\"><IMG SRC=\"$image_path/back_$lang.jpg\" width=78 height=30 alt=\"$str_BACK\" border=0></a>".
#			"<IMG src=\"$image_path/space.jpg\" width=2 height=30>";
#   }
    else{ # "dummy"
      $button[$i] =	"<IMG src=\"$image_path/dummy.jpg\" width=80 height=30>";
    }
  }
  return "<NOBR>$button[0]$button[1]<IMG src=\"$image_path/header.jpg\" width=480 height=30></NOBR><BR>\n";
}

###################################################################################################

sub make_footer
{
  my @arg = @_;
  my $lang = $arg[2];

  my $str_MENU    = &TMSstr::get_str( "MENU"	);
  my $str_SUBMENU = &TMSstr::get_str( "SUBMENU"	);
  #my $str_BACK    = &TMSstr::get_str( "BACK"	);

  my @button = ();

  my $footer_file = 'footer.jpg';
  if( $lang eq 'ja' ){ $footer_file = 'footer_ja.jpg'; }

  my $image_path = 'image';
  unless( -d $image_path ){ $image_path = '../image'; }

  for( my $i=0; $i<=1; $i++ ){
    if( $arg[$i] eq "menu" ){
      $button[$i] =	"<IMG src=\"$image_path/space.jpg\" width=2 height=30>".
			"<a href=\"../\"><IMG SRC=\"$image_path/menu_$lang.jpg\" width=78 height=30 alt=\"$str_MENU\" border=0></a>";
    }
    elsif( $arg[$i] eq "submenu" ){
      $button[$i] =	"<IMG src=\"$image_path/space.jpg\" width=2 height=30>".
			"<a href=\"./\"><IMG SRC=\"$image_path/submenu_$lang.jpg\" width=78 height=30 alt=\"$str_SUBMENU\" border=0></a>";
    }
#   elsif( $arg[$i] eq "back" ){
#     $button[$i] =	"<IMG src=\"$image_path/space.jpg\" width=2 height=30>".
#			"<a href=\"../\"><IMG SRC=\"$image_path/back_$lang.jpg\" width=78 height=30 alt=\"$str_BACK\" border=0></a>";
#   }
    else{ # "dummy"
      $button[$i] =	"<IMG src=\"$image_path/dummy.jpg\" width=80 height=30>";
    }
  }
  return "<NOBR><IMG src=\"$image_path/$footer_file\" width=480 height=30 alt=\"TOYOTA INDUSTRIES CORPORATION\">$button[0]$button[1]</NOBR><BR>\n";
}

###################################################################################################

#sub excel_boot_page
#{
#  my ($xlsfile) = @_;
#
#  my $lang = &TMSstr::get_lang();
#
#  my $title    = &TMSstr::get_str( "NOW_EXCEL_IS_BOOTING" );
#  my $str_BACK = &TMSstr::get_str( "BACK" );
#
#  my $html = 	"<html lang=$lang>\n".
#		"<head>\n".
#		&meta_content_type( $lang ).
#		&meta_no_cache_tag().
#		"<title>$title</title>\n".
#		"<META HTTP-EQUIV=\"Refresh\" CONTENT=\"0; URL=$xlsfile\">\n".
#		"</head>\n".
#		"<body bgcolor=#C7C4E2 onLoad=\"setTimeout('history.back()',10000)\">\n".
#		"<center>\n".
#		"<BR><BR><BR><BR><font size=+1><B>$title</B></font><BR><BR><BR><BR>\n".
#		"<a href=\"javascript:history.back()\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=$str_BACK border=0></a>".
#		"</center>\n".
#		"</BODY></HTML>\n";
#
#  return $html;
#}

###################################################################################################

sub no_data_page
{
  my ($menu_color, $body_color) = @_;

  my $lang = &TMSstr::get_lang();

  my $title    = &TMSstr::get_str( "NO_DATA_FOUND" );
  my $str_BACK = &TMSstr::get_str( "BACK" );
  my $str_NO_DATA_FOUND_IN_THIS_CONDITION = &TMSstr::get_str( "NO_DATA_FOUND_IN_THIS_CONDITION"	);

  my $tbl_width = 630;

  my $html =	"<html lang=$lang>\n".
		"<head>\n".
		&meta_content_type( $lang ).
		&meta_no_cache_tag().
		"<title>$title</title>\n".
		"</head>\n".
		"<body bgcolor=#C7C4E2><center>\n".
		&make_header('menu','dummy', $lang)."<BR>".

		"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
		"<tr align=center bgcolor=$menu_color>\n".
		"<th><font size=+2 color=white>$title</font></th>\n".
		"</tr>\n".
		"<tr align=center bgcolor=$body_color><td>\n".
		"<BR><BR><BR>\n".
		"<font size=+2><B>$str_NO_DATA_FOUND_IN_THIS_CONDITION</B></font>\n".
		"<BR><BR><BR>\n".
		"<A HREF=\"javascript:history.back()\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=$str_BACK border=0></A>\n".
		"<BR><BR><BR><BR>\n".
		"</td></tr>\n".
		"</table><BR>\n".

		&make_footer('dummy','menu', $lang).
		"</center></body></html>\n";
  return $html;
}

###################################################################################################

#use Net::Ping;
#
#sub try_ping
#{
#  my ($host) = @_;
#
#  my $err = 0;
#  my $p = Net::Ping->new("icmp", 0.5);
#  if( ! $p->ping($host) ){ $err = 1; }
#  $p->close();
#  return $err;
#}

###################################################################################################

sub get_temp_num
{
  my $tick = Win32::GetTickCount();
  $tick = sprintf("%07d",($tick % 10000000));  # 下７桁だけを使う（2.7時間で一回り）

  return $tick;
}

# ---------------------------------------------------------

sub get_tmp_file_name
{
  my ($prefix) = @_;

  &make_dir("..\\..\\tmsdata");
  my $tmp_dir = "..\\..\\tmsdata\\temp";
  &make_dir($tmp_dir);

  # 古いファイルの削除
  if( opendir(DIR, $tmp_dir) ){
    my @file_list = readdir(DIR);
    closedir(DIR);

    my $now = time();
    foreach my $file (@file_list){
      #if( $file =~ m/\.tmp$/ ){
      if( $file !~ m/^\./ ){
        my $date = (stat "$tmp_dir\\$file")[9];
        my $diff = $now - $date;
        if( ($diff <= -1800) or (1800 <= $diff) ){  # 30分以上
          unlink("$tmp_dir\\$file");
        }
      }
    }
  }

  return "$tmp_dir\\$prefix". &get_temp_num() .".tmp";
}

# ---------------------------------------------------------

sub get_xlsdata_file_name
{
  my ($prefix, $ext) = @_;

  &make_dir("../../tmsdata");
  my $data_dir = "../../tmsdata/xlsdata";  # HTTP のリンクで使う為 / を使用
  &make_dir($data_dir);

  # 古いファイルの削除
  if( opendir(DIR, $data_dir) ){
    my @file_list = readdir(DIR);
    closedir(DIR);

    my $now = time();
    foreach my $file (@file_list){
      if( $file !~ m/^\./ ){
        my $date = (stat "$data_dir/$file")[9];
        my $diff = $now - $date;
        if( ($diff <= -900) or (900 <= $diff) ){  # 15分以上
          unlink("$data_dir/$file");
        }
      }
    }
  }

  return "$data_dir/$prefix". &get_temp_num() .".$ext";
}

###################################################################################################

sub get_fullpath_url
{
  my ($file) = @_;

  $file =~ s/\\/\//g;
  my @file = split(/\//,$file);

  my $pwd = $ENV{'SCRIPT_NAME'};
  $pwd =~ s/^\///;  # 先頭の / を削除
  my @pwd = split(/\//,$pwd);
  pop @pwd;   # 最後のファイル名を削除

  while( $file[0] eq ".." ){
    shift @file;  # 先頭の要素を削除
    pop @pwd;     # 最後の要素を削除
  }

  my $fullpath = "http://".$ENV{'SERVER_ADDR'};
  if( $ENV{'SERVER_PORT'} ne "80" ){
    $fullpath .= ":".$ENV{'SERVER_PORT'};
  }
  $fullpath .= "/";

  foreach(@pwd ){ $fullpath .= $_."/"; }
  foreach(@file){ $fullpath .= $_."/"; }
  chop $fullpath; # 最後の / を消す

  return $fullpath;
}

# ---------------------------------------------------------

sub get_fullpath_file
{
  my ($file) = @_;

  $file =~ s/\\/\//g;
  my @file = split(/\//,$file);

  my $pwd = Cwd::getcwd();
  my @pwd = split(/\//,$pwd);

  while( $file[0] eq ".." ){
    shift @file;  # 先頭の要素を削除
    pop @pwd;     # 最後の要素を削除
  }

  my $fullpath = "";
  foreach(@pwd ){ $fullpath .= $_."\\"; }
  foreach(@file){ $fullpath .= $_."\\"; }
  chop $fullpath; # 最後の \ を消す

  return $fullpath;
}

###################################################################################################

sub http_header_tmsinf
{
  my ($infofile) = @_;

  print	"Content-Disposition: inline; filename=$infofile\n".
	"Content-type: application/tms-helper\n".
	"\n";
}

###################################################################################################

my $prev_percent; # 経過記憶用

sub disp_percent
{
  my ($total, $count, $phase) = @_;

  if( $count == 0 ){
    if( ! defined($phase) ){ $phase = 0; }

    if( $phase > 0 ){ print &TMSstr::get_str("PHASE")." $phase : 0% .."; }
    else{             print                                  "   0% .."; }

    $prev_percent = 0;
    return;
  }

  if( $total == 0 ){ ++$total; ++$count; }

  my $percent = 100 * $count / $total;
  if( ($prev_percent <  20) && ( 20 <= $percent) ){ print " 20% .."; $prev_percent =  20; }
  if( ($prev_percent <  40) && ( 40 <= $percent) ){ print " 40% .."; $prev_percent =  40; }
  if( ($prev_percent <  60) && ( 60 <= $percent) ){ print " 60% .."; $prev_percent =  60; }
  if( ($prev_percent <  80) && ( 80 <= $percent) ){ print " 80% .."; $prev_percent =  80; }
  if( ($prev_percent < 100) && (100 <= $percent) ){ print " 100% ";  $prev_percent = 100; }
  if( ($prev_percent < 101) && (100 <  $percent) ){ print &TMSstr::get_str("DONE")."\n"; $prev_percent = 101; }
}

###################################################################################################
1;
