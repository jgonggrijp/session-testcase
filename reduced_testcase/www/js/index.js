/*
    (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
    Authors: Julian Gonggrijp, Martijn van der Klis
*/

'use strict';

var app = {
    scope: document.body,
    origin: '',
    
    initialize: function() {
        this.detectBase();
        this.preloadContent();
        $('.reflection-response').each(function() {
            $(this).validate({submitHandler: app.submitReply});
        });
        $('.reflection-captcha').each(function() {
            $(this).validate({submitHandler: app.submitCaptcha});
        });
    },
    
    detectBase: function() {
        this.base = window.location.protocol === 'file:' && this.origin || '';
    },
    
    preloadContent: function() {
        $.get(app.base + '/reflection/').done(function(data) {
            app.loadReflection($('#mirror'), data);
        });
    },
    
    loadReflection: function(page, data) {
        if (data.token) localStorage.setItem('token', data.token);
        app.current_reflection = data.id;
        localStorage.setItem('reflection_data_' + data.id, JSON.stringify(data));
        localStorage.setItem('last_retrieve', data.since);
        page.find('.week-number').html(data.week);
        page.find('.reflection-text').html(data.text);
        page.find('.reflection-discussion').empty();
        _.each(data.responses, function(datum) {
            app.appendReply(page, datum);
        });
        var nickname = localStorage.getItem('nickname');
        if (nickname) page.find('[name="p"]').val(nickname);
        if (data.closure) {
            if (new Date(data.closure) <= new Date()) {
                page.find('.reflection-response').hide();
                page.find('.reflection-closure-announce').hide();
            } else {
                page.find('.reflection-closure-date').text(data.closure);
                page.find('.reflection-closed-notice').hide();
            }
        } else {
            page.find('.reflection-closed-notice').hide();
            page.find('.reflection-closure-announce').hide();
        }
    },

    submitReply: function(form) {
        form = $(form);
        form.hide();
        var page = form.parent(),
            id = app.current_reflection,
            reflection_data = JSON.parse(localStorage.getItem('reflection_data_' + id)),
            nickname = form.find('[name="p"]').val(),
            message = form.find('[name="r"]').val();
        localStorage.setItem('nickname', nickname);
        $.post(app.base + '/reflection/' + id + '/reply', {
            p: nickname,
            r: message,
            t: localStorage.getItem('token'),
            'last-retrieve': localStorage.getItem('last_retrieve'),
            ca: page.find('[name="ca"]').val()
        }).done(function(data) {
            localStorage.setItem('token', data.token);
            switch (data.status) {
            case 'success':
                app.appendReply(page, {
                    pseudonym: nickname,
                    'message': message
                });
                form.find('[name="r"]').val('');
                form.show();
                break;
            case 'ninja':
                page.find('.ninja-message').popup('open', {positionTo: 'window'});
                page.find('.reply-submitted').remove();
                _.each(data.new, function(datum) {
                    app.appendReply(page, datum);
                });
                form.show();
                localStorage.setItem('last_retrieve', data.since);
                break;
            case 'captcha':
                page.find('.captcha-challenge').text(data.captcha_challenge);
                page.find('.captcha-popup').popup('open', {positionTo: 'window'});
            }
        }).fail(function(jqXHR) {
            if ( jqXHR.status == 400 &&
                 jqXHR.responseText && jqXHR.responseText[0] == '{' ) {
                var data = JSON.parse(jqXHR.responseText);
                localStorage.setItem('token', data.token);
                switch (data.status) {
                case 'closed':
                    page.find('.reflection-closed-popup').popup('open', {positionTo: 'window'});
                    page.find('.reflection-closure-announce').hide();
                    page.find('.reflection-closed-notice').show();
                    break;
                case 'invalid':
                    page.find('.reflection-invalid-popup').popup('open', {positionTo: 'window'});
                    page.find('.reflection-response').show();
                }
            }
        });
    },
    
    submitCaptcha: function(form) {
        var page = $(form).parents('[data-role="page"]');
        page.find('.captcha-popup').popup('close');
        app.submitReply(page.find('.reflection-response'));
        $(form).find('[name="ca"]').val('');
    },
    
    appendReply: function(page, data) {
        var upvotes = data.up || 0,
            downvotes = data.down || 0,
            score = app.getScore(upvotes, downvotes);
        var div = $('<div></div>');
        div.addClass('reply-' + (data.id || 'submitted'));
        var date = '<span class="reply-date">' + (data.submission || 'net') + '</span>';
        var pseudonym = '<span class="reply-nick">' + data.pseudonym + '</span>';
        var synopsis = $('<h3 class="reply-synopsis"></h3>').append(date + ' ' + pseudonym);
        div.append(synopsis);
        div.append(date);
        div.append(pseudonym);
        div.append($('<span class="reply-content"></span>').html(data.message));
        if (data.id) {
            div.append('<br>');
            div.append($('<a href="#">good</a>')
                        .addClass('reply-vote ui-btn ui-icon-plus ui-btn-icon-left')
                        .data('for', data.id)
                        .click(function() {
                            app.submitReplyVote(data.id, 'up');
                        }));
            div.append($('<a href="#">bad</a>')
                        .addClass('reply-vote ui-btn ui-icon-minus ui-btn-icon-right')
                        .data('for', data.id)
                        .click(function() {
                            app.submitReplyVote(data.id, 'down');
                        }));
        }
        page.find('.reflection-discussion').append(div);

        // If score is lower than treshold, show the synopsis and display as collapsible.
        if (score < 0.35) {
            synopsis.show();
            page.find('.reply-' + data.id + ' .reply-synopsis .reply-nick').html('spam');
            div.collapsible({ mini: true, collapsedIcon: 'arrow-r', expandedIcon: 'arrow-d' });
        }
        // Otherwise, hide the synopsis.
        else {
            synopsis.hide();
        }
    },

    submitReplyVote: function(id, choice) {
        if (choice === 'up' || choice === 'down') {
            $.post(app.base + '/reply/' + id + '/moderate/', {
                'choice': choice,
                't': localStorage.getItem('token')
            }).done(function(data) {
                localStorage.setItem('token', data.token);
                if (data.status === 'success') {
                    // hide reply vote buttons on success, and add success message
                    $('.reply-' + id + ' .reply-vote').hide();
                    $('.reply-' + id + ' .reply-vote:last')
                        .after($('<em>')
                        .text('Thanks for voting!')
                        .css('color', 'green'));
                }
            });
        }
    },
    
    getScore: function(upvotes, downvotes) {
        var total = upvotes + downvotes;
        if (total === 0) return 1;
        var z = 1.96,
            zz = z * z,
            upObserved = 1.0 * upvotes / total,
            errorTerm = zz / (2 * total),
            sumOfSquares = upObserved * (1 - upObserved) + zz / (4 * total),
            rootTerm = z * Math.sqrt(sumOfSquares / total),
            enumerator = upObserved + errorTerm + rootTerm,
            denominator = 1 + zz / total;
        return enumerator / denominator;
    }
};
