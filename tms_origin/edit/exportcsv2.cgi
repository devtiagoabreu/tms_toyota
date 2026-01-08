#! C:\Perl\bin\perl.exe -I..\common

use strict;
no strict "refs";	# for open($data_fd, "> $fname")
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DirHandle;
use Time::Local;

use TMSstr;
use TMScommon;
use TMSdeny;
use TMSlock;
use TMSstophist;

$| = 1;
require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_EXPORT_CSV_FILE		= &TMSstr::get_str( "EXPORT_CSV_FILE"		);
my $str_SHIFT_DATA		= &TMSstr::get_str( "SHIFT_DATA"		);
my $str_STOP_HISTORY		= &TMSstr::get_str( "STOP_HISTORY"		);
my $str_OPERATOR_DATA		= &TMSstr::get_str( "OPERATOR_DATA"		);
my $str_YARN_INVENTORY_FORECAST	= &TMSstr::get_str( "YARN_INVENTORY_FORECAST"	);
my $str_DONE			= &TMSstr::get_str( "DONE"			);
my $str_EXPORT_DONE		= &TMSstr::get_str( "EXPORT_DONE"		);

if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $html = new CGI;

my @shift_month_list    = $html->param('shift');
my @operator_month_list = $html->param('operator');
my @history_month_list  = $html->param('history');
my $forecast            = $html->param('forecast');

my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

if( ($#shift_month_list < 0) && ($#operator_month_list < 0) && ($#history_month_list < 0) && (length($forecast) == 0) ){
 print &TMScommon::no_data_page( $menu_color, $body_color );
 exit;
}

my $update_lock = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::check_lockfile($update_lock,$ENV{REMOTE_ADDR},\$other_user) ){  # データ更新中は使用不可
  print &TMSlock::data_updating_page( $other_user );
  exit;
}

my $lockfile = 'exportcsv.lock';
if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20,\$other_user) ){	 # 同時使用を禁止（レベル１）
  print &TMSlock::operation_lock_page( $other_user );
  exit;
}
my $lock_start = time();	# ロック開始時間


my $title = $str_EXPORT_CSV_FILE;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function move_next_page() {\n".
	"    location.href = \"exportcsv3.cgi\";\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=$body_color OnLoad=\"setTimeout('move_next_page()',2000)\">\n".
	"<pre>\n";

my $tmsdata_dir  = "..\\..\\tmsdata";
my $current_dir  = "$tmsdata_dir\\current";
my $shift_dir    = "$tmsdata_dir\\shift";
my $operator_dir = "$tmsdata_dir\\operator";

my $csv_dir = "\\TMSDATA";

my @shift_id = &TMScommon::get_shift_id();

my $data_fd = "FILE";		# &open_data_file() 用
my $data_fname = "";		#


&TMScommon::make_dir($csv_dir);

if( $#shift_month_list >= 0 ){
  print "<B>$str_SHIFT_DATA</B>\n";
  &make_shift_csv();
}

if( $#operator_month_list >= 0 ){
  print "<B>$str_OPERATOR_DATA</B>\n";
  &make_operator_csv();
}

if( $#history_month_list >= 0 ){
  &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);  # ロックファイルを更新（レベル１）
  print "<B>$str_STOP_HISTORY</B>\n";
  &make_history_update_list( @history_month_list );
  &TMSstophist::make_stophist_csv( 0 );
}

if( $forecast eq "on" ){
  print "<B>$str_YARN_INVENTORY_FORECAST</B>\n";
  &make_forecast_csv();
}

print	"<B>**** $str_EXPORT_DONE ****</B>\n".
	"</pre>\n".
	"</body></html>\n";

unlink($lockfile);	# ロックファイルを削除

exit;

###################################################################################################
#
# 補足：常に、$data_fd eq "FILE" となるのは、バグ修正を少ない変更で行う為の暫定処置であり、
#       時間に余裕がある時に修正しても良い。 2009/12/09

sub open_data_file
{
  my ($fname) = @_;

  # 前回と同じなら、何もしない。
  if( $data_fname eq $fname ){ return $data_fd; }

  # 前回のファイルを閉じる
  &close_data_file();

  # 新しいファイルを開く
  if( open($data_fd, "> $fname") ){ $data_fname = $fname; }
  else{ $data_fname = ""; }

  return $data_fd;
}

# -------------------------------------------------------------------------

sub close_data_file
{
  if( $data_fname ne "" ){
    close($data_fd);
  }
  $data_fname = "";
}

###################################################################################################

sub make_shift_csv
{
  my $dir = new DirHandle $shift_dir;	# ディレクトリのファイルリストを取得する
  my @file = ();			# dirの結果を配列に入れる
  while( my $f = $dir->read ){
    foreach(@shift_month_list){
      my $mstr = $_;		# foreach で読み出した変数を直接変更してはダメ！！
      $mstr =~ s/\./\\./g;	# 月の . をエスケープする。
     if( $f =~ m/^$mstr\.\d{2}\.\d\.txt$/ ){ push(@file,$f); last; }
    }
  }
  $dir->close;
  @file = sort @file; # ソートする

  ### 経過表示 ###
  my $total = ($#shift_month_list + 1) * 2;  # １ループで２回カウントUPする為
  my $count=0;
  &TMScommon::disp_percent($total, $count);  # 経過表示（開始）

  foreach my $month (@shift_month_list){
    my @m = split(/\./,$month);
    my $dname = "$csv_dir\\$m[0]-$m[1]";
    &TMScommon::make_dir($dname);
    my $d_dname = "$dname\\daily";
    my $m_dname = "$dname\\machine";
    &TMScommon::make_dir($d_dname);
    &TMScommon::make_dir($m_dname);

    # daily CSVファイル生成 ＆ machine 中間ファイルを生成 --------------------------------

    open( MAC, "> $dname\\machine.tmp" );

    my $mstr = $month;		# foreach で読み出した変数を直接変更してはダメ！！
    $mstr =~ s/\./\\./g;	# 月の . をエスケープする。

    foreach my $fname ( @file ){
      if( $fname =~ m/^$mstr\.([^.]+)/ ){
        my @s = split(/\./,$fname);
        my $day = "$s[0]-$s[1]-$s[2]";
        if( open(IN,"< $shift_dir\\$fname") ){
          while(<IN>){
            if( m/,mac_name ([^,]+)/){
              my $mac = $1;
              $mac =~ s/[ \\\/:,;*?"<>|]/_/g;		# ファイル名に使え無い文字を _ に変換

              my $csv = &make_monitor_data( \$_, "shift" );
              print MAC $mac.",".$csv;

              my $fd = &open_data_file( "$d_dname\\$day.csv" );
              print $fd $csv;
            }
          }
          close(IN);

          my $now = time();
          if( ($now - $lock_start) >= 10 ){	# 処理開始して１０秒経過したら。
            $lock_start = $now;
            &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）
          }

        }
      }
    }
    &close_data_file();

    close(MAC);

    &TMScommon::disp_percent($total, ++$count);  # 経過表示（途中１）

    # machine CSVファイル ------------------------------------------------------------

    # データーをソートする。
    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）
    # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
    system( "sort $dname\\machine.tmp /O $dname\\machine_sort.tmp" );

    # データーを分割する。
    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）
    open( MAC, "< $dname\\machine_sort.tmp" );
    while(<MAC>){
      my @csv = split(/,/,$_,2);
      my $fd = &open_data_file( "$m_dname\\$csv[0].csv" );
      print $fd $csv[1];
    }
    &close_data_file();
    close(MAC);

    unlink("$dname\\machine.tmp");
    unlink("$dname\\machine_sort.tmp");

    &TMScommon::disp_percent($total, ++$count);  # 経過表示（途中２）
  }

  &TMScommon::disp_percent(100,101);  # 経過表示（終了）

}

###################################################################################################

sub make_operator_csv
{
  my $dir = new DirHandle $operator_dir;	# ディレクトリのファイルリストを取得する
  my @file = ();				# dirの結果を配列に入れる
  while( my $f = $dir->read ){
    foreach(@operator_month_list){
      my $mstr = $_;		# foreach で読み出した変数を直接変更してはダメ！！
      $mstr =~ s/\./\\./g;	# 月の . をエスケープする。
     if( $f =~ m/^$mstr\.\d{2}\.txt$/ ){ push(@file,$f); last; }
    }
  }
  $dir->close;

  my $total = ($#operator_month_list + 1) * 2;  # １ループで２回カウントUPする為
  my $count=0;
  &TMScommon::disp_percent($total, $count);  # 経過表示（開始）

  foreach my $month (@operator_month_list){
    my @m = split(/\./,$month);
    my $dname = "$csv_dir\\$m[0]-$m[1]";
    &TMScommon::make_dir($dname);
    my $o_dname = "$dname\\operator";
    &TMScommon::make_dir($o_dname);

    # operator 中間ファイルを生成 ------------------------------------------------

    open( OPE, "> $dname\\operator.tmp" );

    my $mstr = $month;		# foreach で読み出した変数を直接変更してはダメ！！
    $mstr =~ s/\./\\./g;	# 月の . をエスケープする。

    foreach my $fname ( @file ){
      if( $fname =~ m/^$mstr.([^.]+)/ ){
        if( open(IN,"< $operator_dir\\$fname") ){
          while(<IN>){
            if( m/,ope_name ([^,]+)/){
              my $ope = $1;
              $ope =~ s/[ \\\/:,;*?"<>|]/_/g;	# ファイル名に使え無い文字を _ に変換

              my $csv = &make_monitor_data( \$_, "operator" );
              print OPE $ope.",".$csv;
            }
          }
          close(IN);

          my $now = time();
          if( ($now - $lock_start) >= 10 ){	# 処理開始して１０秒経過したら。
            $lock_start = $now;
            &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）
          }

        }
      }
    }

    close(OPE);

    &TMScommon::disp_percent($total, ++$count);  # 経過表示（途中１）

    # operator CSVファイル ------------------------------------------------------------

    # データーをソートする。
    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）
    # (参考)コマンドライン文字数は 2047文字(NT,2000) 8191文字(XP) までOK
    system( "sort $dname\\operator.tmp /O $dname\\operator_sort.tmp" );

    # データーを分割する。
    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）
    open( OPE, "< $dname\\operator_sort.tmp" );
    while(<OPE>){
      my @csv = split(/,/,$_,2);
      my $fd = &open_data_file( "$o_dname\\$csv[0].csv" );
      print $fd $csv[1];
    }
    &close_data_file();
    close(OPE);

    unlink("$dname\\operator.tmp");
    unlink("$dname\\operator_sort.tmp");

    &TMScommon::disp_percent($total, ++$count);  # 経過表示（途中２）
  }

  &TMScommon::disp_percent(100,101);  # 経過表示（終了）
}

###################################################################################################

sub make_monitor_data
{
  my ($r_line,$mode) = @_;

  $$r_line =~ s/\n$//;	# 改行コードを削除。
# $$r_line =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  my @list = split(/,/,$$r_line);

  my %tmp = ();
  foreach(@list){
    my @data = split(/ /,$_,2);
    if( $#data >= 1 ){ $tmp{$data[0]} = $data[1]; }
  }

  my $shift_name = "";
  my $ope_name   = "";
  my $day        = "";
  if( $mode eq "shift" ){
    my @sd = split(/\./,$tmp{"shift"});
    $shift_name = "$sd[0].$sd[1].$sd[2].$shift_id[$sd[3]]";
  }
  else{ # "operator"
    $ope_name   = $tmp{"ope_name"};
    $day        = $tmp{"day"};
  }

  my $mac_name   = $tmp{"mac_name"};

  my $mac_type = "JAT";  # 旧データ用のデフォルト
  if( exists($tmp{"mac_type"}) ){ $mac_type = $tmp{"mac_type"}; }

  my $style_name = $tmp{"style"};
  my $beam       = $tmp{"beam"};
  my $ubeam      = $tmp{"ubeam"};
  my @seisan     = split(/ /,$tmp{"seisan"});
  my $run_tm     = $tmp{"run_tm"};
  my $stop_ttm   = $tmp{"stop_ttm"};
  my @s_ct       = split(/ /,$tmp{"s_ct"});
  my @s_tm       = split(/ /,$tmp{"s_tm"});

  my @stop_ct    = ();
  my @stop_tm    = ();
  my @wf1_ct     = ();
  my @wf1_tm     = ();
  my @wf2_ct     = ();
  my @wf2_tm     = ();
  my @lh_ct      = ();
  my @lh_tm      = ();

  if( $mac_type eq "LWT" ){
    &TMScommon::get_detail_stop_lwt(\@s_ct, \@stop_ct, \@wf1_ct, \@wf2_ct, \@lh_ct);
    &TMScommon::get_detail_stop_lwt(\@s_tm, \@stop_tm, \@wf1_tm, \@wf2_tm, \@lh_tm);
  }else{  # JAT
    &TMScommon::get_detail_stop_jat(\@s_ct, \@stop_ct, \@wf1_ct, \@wf2_ct, \@lh_ct);
    &TMScommon::get_detail_stop_jat(\@s_tm, \@stop_tm, \@wf1_tm, \@wf2_tm, \@lh_tm);
  }

  # 表示形式
  my $rpm;
  if( $run_tm <= 0 ){ $rpm = 0; }
  else{ $rpm = sprintf("%d", ($seisan[0]*100)/($run_tm/60) ); }

  my $effic;
  if( ($run_tm + $stop_ttm) <= 0 ){ $effic = "0.00"; }
  else{ $effic = sprintf("%1.2f", ($run_tm*100)/($run_tm + $stop_ttm) ); }

  $run_tm   = sprintf("%1.2f",($run_tm/60));
  $stop_ttm = sprintf("%1.2f",($stop_ttm/60));
  $seisan[0] = sprintf("%1.1f",($seisan[0]/10));
  $seisan[1] = sprintf("%1.1f",($seisan[1]/10));
  $seisan[2] = sprintf("%1.1f",($seisan[2]/10));
  for( my $i=0; $i<=$#stop_tm; $i++ ){ $stop_tm[$i] = sprintf("%1.2f",($stop_tm[$i]/60)); }
  for( my $i=0; $i<=$#wf1_tm;  $i++ ){ $wf1_tm[$i]  = sprintf("%1.2f",($wf1_tm[$i]/60));  }
  for( my $i=0; $i<=$#wf2_tm;  $i++ ){ $wf2_tm[$i]  = sprintf("%1.2f",($wf2_tm[$i]/60));  }
  for( my $i=0; $i<=$#lh_tm;   $i++ ){ $lh_tm[$i]   = sprintf("%1.2f",($lh_tm[$i]/60));   }

  # 不要データの削除
  if( $mac_type eq "LWT" ){
    for( my $i=3; $i<=5; $i++ ){  # Color4～6
      $wf1_ct[$i] = ""; $wf1_tm[$i] = "";
      $wf2_ct[$i] = ""; $wf2_tm[$i] = "";
      $lh_ct[$i]  = ""; $lh_tm[$i]  = "";
    }
  }else{  # JAT
    $stop_ct[11] = "";  # ＣＣ後
    $stop_tm[11] = "";  #
  }

  # ＣＳＶ出力
  my $csv;
  if( $mode eq "shift" ){ $csv =  "$shift_name";    }
  else{                   $csv =  "$ope_name,$day"; } # "operator"

  $csv .= ",$mac_name,$style_name,$ubeam,$beam,$rpm,$effic,$run_tm,$stop_ttm";
  $csv .= ",$seisan[0],$seisan[1],$seisan[2],$seisan[3]";

  for( my $i=0; $i<=10; $i++ ){ $csv .= ",$stop_ct[$i],$stop_tm[$i]"; }

  for( my $i=0; $i<=$#wf1_ct; $i++ ){ $csv .= ",$wf1_ct[$i],$wf1_tm[$i]"; }

  for( my $i=0; $i<=$#wf2_ct; $i++ ){ $csv .= ",$wf2_ct[$i],$wf2_tm[$i]"; }

  for( my $i=0; $i<=$#lh_ct; $i++ ){ $csv .= ",$lh_ct[$i],$lh_tm[$i]"; }

  $csv .= ",$stop_ct[11],$stop_tm[11]";  # LWT710対応で追加（ＣＣ後）

  $csv .= "\n";

  return $csv;
}

###################################################################################################

sub make_forecast_csv
{
  &TMScommon::disp_percent(100,0); # 0%

  &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);  # ロックファイルを更新（レベル１）

  &TMScommon::disp_percent(100,20); # 20%

  if( open(IN,  "< $current_dir\\current.txt") ){
    open(OUT, "> $csv_dir\\forecast.csv");

    while(<IN>){
      print OUT &make_forecast_data( \$_ );
    }

    close(OUT);
    close(IN);
  }

  &TMScommon::disp_percent(100,101); # 100% done

}

###################################################################################################

sub make_forecast_data
{
  my ($r_line) = @_;

  $$r_line =~ s/\n$//;	# 改行コードを削除。
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

  $r_beam[0] = sprintf("%1.1f",($r_beam[0]/10));
  $r_beam[1] = sprintf("%1.1f",($r_beam[1]/10));

  $s_ubeam[0] = sprintf("%1.1f",($s_ubeam[0]/10));
  $s_ubeam[1] = sprintf("%1.1f",($s_ubeam[1]/10));

  $r_ubeam[0] = sprintf("%1.1f",($r_ubeam[0]/10));
  $r_ubeam[1] = sprintf("%1.1f",($r_ubeam[1]/10));

  {
    my ($sec,$min,$hour,$mday,$mon,$year);
    my $get_date;

    my @data = split(/ /,$get_time);
    $get_time = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $data[0],$data[1],$data[2],$data[4],$data[5],$data[6]);

    $get_date = timelocal($data[6],$data[5],$data[4],$data[2],($data[1] -1),($data[0] -1900));

    ($sec,$min,$hour,$mday,$mon,$year) = localtime($get_date+($doff_fcst*60));
    $doff_fcst = sprintf("%04d/%02d/%02d %02d:%02d:00",($year+1900),($mon+1),$mday,$hour,$min);

    ($sec,$min,$hour,$mday,$mon,$year) = localtime($get_date+($wout_fcst*60));
    $wout_fcst = sprintf("%04d/%02d/%02d %02d:%02d:00",($year+1900),($mon+1),$mday,$hour,$min);

    ($sec,$min,$hour,$mday,$mon,$year) = localtime($get_date+($uwout_fcst*60));
    $uwout_fcst = sprintf("%04d/%02d/%02d %02d:%02d:00",($year+1900),($mon+1),$mday,$hour,$min);
  }

  my $csv  = "$mac_name,$style,$cut_len[0],$cut_len[1],$cut_len[2],$cut_len[3]";
  $csv .= ",$cloth_len[0],$cloth_len[1],$cloth_len[2],$cloth_len[3],$doff_fcst";

  $csv .= ",$ubeam,$s_ubeam[0],$s_ubeam[1]";
  $csv .= ",$r_ubeam[0],$r_ubeam[1],$uwout_fcst";

  $csv .= ",$beam,$s_beam[0],$s_beam[1]";
  $csv .= ",$r_beam[0],$r_beam[1],$wout_fcst";
  $csv .= ",$get_time\n";

  return $csv;
}

###################################################################################################
# 機能   : 要求年月に属する停台履歴元フォルダの一覧を
#            要求ファイルに書き込み
# 引数   : 要求年月の一覧
# 戻り値 : なし

sub make_history_update_list
{
  my ( @req_month_list ) = @_;

  # 対象月か判定用にハッシュを作る
  my %req_month = ();  # yyyy.mm
  foreach( @req_month_list ){ $req_month{$_} = 1; }

  # 停止履歴フォルダの一覧を取得
  my ($stophist_dir, @stophist_subdir) = &TMSstophist::get_stophist_dir();

  # 要求月に対応する停止履歴データフォルダ一覧を作成
  my @update_list = ();  # yyyy.mm.dd
  foreach my $subdir ( @stophist_subdir ){
    my $ym = substr( $subdir, 0, 7 ); # yyyy.mmの部分を取得
    if( exists($req_month{$ym}) ){
      push( @update_list, $subdir );
    }
  }

  my $update_txt = "$stophist_dir\\history_update.txt";

  # 古いファイルを消す
  if( -f $update_txt ){ unlink( $update_txt); }

  # フィイルに書き出す
  if( $#update_list >= 0 ){
    if( open(LST,"> $update_txt") ){
      foreach( @update_list ){ print LST "$_\n"; }
      close(LST);
    }
  }

  return;
}

###################################################################################################
1;
