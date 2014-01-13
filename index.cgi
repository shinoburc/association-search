#!/usr/bin/perl

use CGI;
use LWP;
use HTML::TreeBuilder::XPath qw();
use WWW::Wikipedia;
use Text::MeCab;
use HTML::Entities;

my $cgi = new CGI;
print $cgi->header(-charset=>"utf-8");

my $title = "Association Search";

#&mecab('perl', 'q', 'r');
#exit;

if(defined $cgi->param('action')){
  &mecab($cgi->param('q'), $cgi->param('qid'), $cgi->param('rid'));
} else {
  &print_index;
}

sub mecab($$$){
  my $q = shift;
  my $qid = shift;
  my $rid = shift;
  my %querys = ();

  return if $q eq "";

  my $text = "";
  my $wiki = WWW::Wikipedia->new();
  foreach my $query(split(/ /,$q)){
    $querys{$query} = 1;
    #my $result = $wiki->search( $query );
    if ( $result ) {
      #$result->language( 'ja' );
      $text .= $result->text();
    }
    # list any related items we can look up
    # print join( "\n", $result->related() );
  }

  my $ua = LWP::UserAgent->new;
  $ua->agent('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0;');
  my $request = HTTP::Request->new('GET' , 'http://www.google.co.jp/search?num=100&q=' . $q);
  my $response = $ua->request($request);

  my $tree = HTML::TreeBuilder::XPath->new;
  $tree->parse($response->content);

  for my $node ($tree->findnodes('//h3[@class = "r"]')) {
    $text .= $_->as_text() for @{ $node->content_array_ref };
  }
  for my $node ($tree->findnodes('//span[@class = "st"]')) {
    $text .= $node->as_text;
  }

  my $m = Text::MeCab->new();
  my $n = $m->parse($text);

  my %keywords = {};
  while ($n) {
    my @features = split(/,/, $n->feature);
    # 国      名詞,普通名詞,*,*,国,こく,*     43138243<br />
    # reference /home/dot/work/kurobox/work/cbot/module/relation.pl
    if(@features[0] eq "名詞"){
      if(exists $keywords{$n->surface}){
        $keywords{$n->surface}++;
      } else {
        $keywords{$n->surface} = 1;
      }
    }
    $n = $n->next;
  }

  my $i = 0;
  print '<ul>';
  AJAX_OUTPUT_LOOP:
  foreach my $keyword(sort { $keywords{$b} <=> $keywords{$a} } keys %keywords){
      next if $keywords{$keyword} < 20;
      next if exists $querys{$keyword};
      next if exists $querys{uc($keyword)};
      next if exists $querys{lc($keyword)};
      next if exists $querys{ucfirst(lc($keyword))};
      foreach my $query(keys(%querys)){
        next AJAX_OUTPUT_LOOP if $query =~ /$keyword/;
      }

      print '<li style="list-style-type:none">';
      printf '<input type="button" id="%s" value="%s" onClick="search(\'%s\', \'%s\')" style="font-size: %sem"/>', $qid . '-' . $i, escape($keyword), $qid . '-' . $i, $rid . '-' . $i, $keywords{$keyword}/20;
      #printf '<input type="button" value="google" onClick="google(\'%s\')"/>', $qid . '-' . $i;
      printf '<a href="http://www.google.com/#q=%s" target="_blank"><img src="http://www.google.co.jp/favicon.ico" width="20" height="20"/></a>', escape($q) . ' ' . escape($keyword);
      print '</li>';
      printf '<div id="%s"></div>', $rid . '-' . $i;
      $i++;
  }
  print '</ul>';
}

sub escape($){
  my $str = shift;
  return encode_entities($str, q{&<>"'});
  #return encode_entities($str, "<>&");
}

sub print_index(){
  print <<"_HTML_";
<!DOCTYPE html>
<html class="no-js">
  <head>
    <meta charset='utf-8' />
    <title>Developers Convention - $title</title>
    <script src="as.js" type="text/javascript"></script>
  </head>
  <body style="margin: 0; padding: 0;">
  <div id="site_bar" style="margin: 0px auto; background: #E00; color: #FFF;padding: 2px 15px 2px 15px;">
    <center>
    <a href="/dc"><img src="../img/DevelopersConvention.png" /></a>
    </center>
    <a href="/dc/naming" style="color: #FFF;">Naming</a>
    &nbsp;
    <a href="/dc/as" style="color: #FFF;">Association Search</a>
    &nbsp;
    <a href="/dc/cs" style="color: #FFF;">Code Snippet</a>
    &nbsp;
    <a href="/dc/db" style="color: #FFF;">DB</a>
    &nbsp;
    <a href="/dc/wiki" style="color: #FFF;">Wiki</a>
  </div>

  <!--
  <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <path stroke="#000" stroke-width="2" fill="none" d="M 818 110 C 836 110 836 182 854 182"></path>
  </svg>
  -->
  <div align="center" class="search_form">
    <div class="search_title">
      <h2>
        <img src="/favicon.ico" width="40" height="40" />
        $title
      </h2>
    </div>
    <div class="search_form">
      <input type="text" size="100" id="q" onKeyPress="enter()" />
      <br />
      <br />
      <input type="button" value="search" onClick="search('q', 'r')"/>
      <input type="button" value="google" onClick="google('q')"/>
      <input type="button" value="I'm Feeling Rocky" onClick="rocky()"/>
      <input type="hidden" name="json" id="json" value="" />
    </div>
  </div>

  <div id="r">
  </div>

  </body>
</html>
_HTML_
}
