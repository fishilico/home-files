use strict;

use vars qw($VERSION %IRSSI);
$VERSION = '2009051301';
%IRSSI = (
	authors		=> 'Raphaël Barrois',
	contact		=> 'xelnor@xelnor.net',
	name		=> 'prevtopic',
	description	=> 'reminds what the previous topic was on topic changes',
);

use Irssi 20020324;
use vars qw(%prevtopics);

sub sig_channel_topic_changed ($) {
	my ($channel) = @_;
	my $ircnet = $channel->{server}->{tag};
	my $name = $channel->{name};

	# Time
	my ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime($channel->{topic_time});
	my $newtime = ($mday < 10 ? "0$mday" : $mday)."/".($mon + 1 < 10 ? "0".($mon + 1) : $mon + 1)."/".($year + 1900)." ".($hour < 10 ? "0$hour" : $hour).":".($min < 10 ? "0$min" : $min).":".($sec < 10 ? "0$sec" : $sec);

	# Data
	my $data = {'topic'		=> $channel->{topic},
				'topic_by'	=> $channel->{topic_by},
				'topic_time'=> $newtime
			};
	my $prev = $prevtopics{$ircnet}{$name};
	$prevtopics{$ircnet}{$name} = $data;
	return if ($prev->{'topic'} eq $channel->{topic});
	return if ($prev->{'topic'} eq '');

	$channel->print("          %KTopic was : %n".$prev->{'topic'}."%K (set by %U".$prev->{'topic_by'}."%U on ".$prev->{'topic_time'}.")", MSGLEVEL_CRAP);
}

Irssi::signal_add('channel topic changed', \&sig_channel_topic_changed);
sig_channel_topic_changed($_) foreach(Irssi::channels());
