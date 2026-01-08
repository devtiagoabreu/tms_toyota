#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Time::Local;

use TMSstr;
use TMScommon;
use TMSlock;
use TMSselitem;

#require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $menu_color = '#426AB3';
my $body_color = '#E1E2F2';

my $html = new CGI;

my $sel_mode = $html->param('sel_mode');

my %loom  = ();
my %style = ();
if( $sel_mode eq 'loom' ){
  my @p = $html->param('loom');
  if( $#p < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
  foreach(@p){ $loom{$_} = 1; }
} else{
  my @p = $html->param('style');
  if( $#p < 0 ){
    require '../common/http_header.pm';
    print &TMScommon::no_data_page( $menu_color, $body_color );
    exit;
  }
  foreach(@p){ $style{$_} = 1; }
}

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){	# データ更新中は使用不可
  require '../common/http_header.pm';
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

# 各ファイル名の取得
my $xlsfile = "../xlsfile/$lang/forecast.xls";

my $datafile = &TMScommon::get_xlsdata_file_name("forecast","csv");

my $infofile = "forecast.tmshlp";


# ＣＳＶファイルの出力
my $val_c_unit    = &TMSselitem::get_value_of_unit();
my $val_b_unit    = &TMSselitem::get_value_of_beam_unit();
my $val_beam_type = &TMSselitem::get_value_of_beam_type();

my $ttl_c_unit   = &TMSselitem::get_title_of_unit();
my $ttl_b_unit   = &TMSselitem::get_title_of_beam_unit();


my $now_date = &TMScommon::get_now_date();

open(OUT, "> $datafile" );
print OUT	"( $now_date )\n".
		"\n";

print OUT &make_forecast_title(	$sel_mode,
				$ttl_c_unit,
				$ttl_b_unit,
				$val_beam_type  );

my $dcount = 0;
open(IN,'< ../../tmsdata/current/current.txt');
while(<IN>){
  my $line = $_;
  my $m = 0;
  if( $sel_mode eq "loom" ){
    if( $line =~ m/,mac_name ([^,]+)/ ){
      if( exists($loom{$1}) ){ $m = 1; }
    }
  } else{  # "style"
    if( $line =~ m/,style ([^,]+)/ ){
      if( exists($style{$1}) ){ $m = 1; }
    }
  }

  if( $m ){
    $dcount++;
    print OUT &make_forecast_data(	$sel_mode,
					\$line,
					$val_c_unit,
					$val_b_unit,
					$val_beam_type  );
  }
}
close(IN);
close(OUT);


if( $dcount == 0 ){
  require '../common/http_header.pm';
  print &TMScommon::no_data_page( $menu_color, $body_color );
}
else{
  # TmsHelper.exe 用情報データ出力
  &TMScommon::http_header_tmsinf($infofile);

  print "method POPUP_EXCEL\n";
  print "version 1.0\n";

  print "xlsfile ". &TMScommon::get_fullpath_url($xlsfile). "\n";

  if( $ENV{REMOTE_ADDR} eq '127.0.0.1' ){  # ローカルの場合（データ読み込み高速化の為）
    print "csvfile1 ". &TMScommon::get_fullpath_file($datafile). "\n";
  }else{  # リモートの場合
    print "csvfile1 ". &TMScommon::get_fullpath_url($datafile). "\n";
  }

  #print "macro start_make_all\n";
}

exit;

###################################################################################################

sub make_forecast_title
{
  my ( $sel, $c_unit, $b_unit, $beam_type ) = @_;

  my $htdata =	"";

  if( $sel eq "loom" ){
    $htdata .=	"LOOM,STYLE";
  } else{
    $htdata .=	"STYLE,LOOM";
  }
  $htdata .=	",DOFF_LENGTH&$c_unit".
		",CLOTH_LENGTH&$c_unit".
		",DOFF_FORECAST&YMD_HM";

  if( $beam_type == 2 ){
    $htdata .=	",TOP_BEAM".
		",TOP_BEAM_SET&$b_unit".
		",TOP_BEAM_REMAIN&$b_unit".
		",TOP_BEAM_FORECAST&YMD_HM";
  }

  $htdata .=	",BEAM".
		",BEAM_SET&$b_unit".
		",BEAM_REMAIN&$b_unit".
		",BEAM_FORECAST&YMD_HM".

		",DATA_DATE&YMD_HM\n";

  return $htdata;
}

###################################################################################################

sub make_forecast_data
{
  my ( $sel, $r_line, $c_unit, $b_unit, $beam_type ) = @_;

  $$r_line =~ s/\n$//;		# 改行コードを削除。
# $$r_line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  my $mac_name   = $tmp{"mac_name"};
  my $style      = $tmp{"style"};
  my @cut_len    = split(/ /,$tmp{"cut_len"});
  my @cloth_len  = split(/ /,$tmp{"cloth_len"});
  my $doff_fcst  = $tmp{"doff_fcst"};
  my $beam       = $tmp{"beam"};
  my @s_beam     = split(/ /,$tmp{"s_beam"});
  my @r_beam     = split(/ /,$tmp{"r_beam"});
  my $wout_fcst  = $tmp{"wout_fcst"};
  my $ubeam      = $tmp{"ubeam"};
  my @s_ubeam    = split(/ /,$tmp{"s_ubeam"});
  my @r_ubeam    = split(/ /,$tmp{"r_ubeam"});
  my $uwout_fcst = $tmp{"uwout_fcst"};
  my $get_time   = $tmp{"get_time"};

  $cut_len[0] = sprintf("%1.1f",($cut_len[0]/10));
  $cut_len[1] = sprintf("%1.1f",($cut_len[1]/10));
  $cut_len[2] = sprintf("%1.1f",($cut_len[2]/10));

  $cloth_len[0] = sprintf("%1.1f",($cloth_len[0]/10));
  $cloth_len[1] = sprintf("%1.1f",($cloth_len[1]/10));
  $cloth_len[2] = sprintf("%1.1f",($cloth_len[2]/10));

  $s_beam[0] = sprintf("%1.1f",($s_beam[0]/10));
  $s_beam[1] = sprintf("%1.1f",($s_beam[1]/10));
  $s_beam[2] = sprintf("%1.1f",($s_beam[2]/10));

  $r_beam[0] = sprintf("%1.1f",($r_beam[0]/10));
  $r_beam[1] = sprintf("%1.1f",($r_beam[1]/10));
  $r_beam[2] = sprintf("%1.1f",($r_beam[2]/10));

  $s_ubeam[0] = sprintf("%1.1f",($s_ubeam[0]/10));
  $s_ubeam[1] = sprintf("%1.1f",($s_ubeam[1]/10));
  $s_ubeam[2] = sprintf("%1.1f",($s_ubeam[2]/10));

  $r_ubeam[0] = sprintf("%1.1f",($r_ubeam[0]/10));
  $r_ubeam[1] = sprintf("%1.1f",($r_ubeam[1]/10));
  $r_ubeam[2] = sprintf("%1.1f",($r_ubeam[2]/10));

  {
    my ($sec,$min,$hour,$mday,$mon,$year);
    my $get_date;

    my @data = split(/ /,$get_time);
    $get_time = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $data[0],$data[1],$data[2],$data[4],$data[5],$data[6]);

    $get_date = timelocal($data[6],$data[5],$data[4],$data[2],($data[1] -1),($data[0] -1900));

    ($sec,$min,$hour,$mday,$mon,$year) = localtime($get_date+($doff_fcst*60));
    $doff_fcst = sprintf("%04d/%02d/%02d %02d:%02d:00",($year+1900),($mon+1),$mday,$hour,$min);

    ($sec,$min,$hour,$mday,$mon,$year) = localtime($get_date+($uwout_fcst*60));
    $uwout_fcst = sprintf("%04d/%02d/%02d %02d:%02d:00",($year+1900),($mon+1),$mday,$hour,$min);

    ($sec,$min,$hour,$mday,$mon,$year) = localtime($get_date+($wout_fcst*60));
    $wout_fcst = sprintf("%04d/%02d/%02d %02d:%02d:00",($year+1900),($mon+1),$mday,$hour,$min);
  }

  my $htdata =	"";

  if( $sel_mode eq "loom" ){
    $htdata .=	"=\"$mac_name\",=\"$style\"";
  } else{
    $htdata .=	"=\"$style\",=\"$mac_name\"";
  }
  $htdata .=	",$cut_len[$c_unit]".
		",$cloth_len[$c_unit]".
		",$doff_fcst";

  if( $beam_type == 2 ){
    $htdata .=	",=\"$ubeam\"".
		",$s_ubeam[$b_unit]".
		",$r_ubeam[$b_unit]".
		",$uwout_fcst";
  }

  $htdata .=	",=\"$beam\"".
		",$s_beam[$b_unit]".
		",$r_beam[$b_unit]".
		",$wout_fcst".

  		",$get_time\n";

  return $htdata;
}
###################################################################################################

