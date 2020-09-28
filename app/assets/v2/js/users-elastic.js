let users = [];
let usersPage = 1;
let usersNumPages = '';
let usersHasNext = false;
let numUsers = '';
let hackathonId = document.hasOwnProperty('hackathon_id') ? document.hackathon_id : '';

Vue.mixin({
  methods: {
    messageUser: function(handle) {
      let vm = this;
      const url = handle ? `${vm.chatURL}/hackathons/messages/@${handle}` : `${vm.chatURL}/`;

      chatWindow = window.open(url, 'Loading', 'top=0,left=0,width=400,height=600,status=no,toolbar=no,location=no,menubar=no,titlebar=no');
    },

    fetchUsers: function(newPage) {
      let vm = this;

      vm.isLoading = true;
      vm.noResults = false;

      if (newPage) {
        vm.usersPage = newPage;
      }
      vm.params.page = vm.usersPage;

      if (vm.searchTerm) {
        vm.params.search = vm.searchTerm;
      } else {
        delete vm.params['search'];
      }

      if (vm.hideFilterButton) {
        vm.params.persona = 'tribe';
      }

      if (vm.params.persona === 'tribe') {
        // remove filters which do not apply for tribes directory
        delete vm.params['rating'];
        delete vm.params['organisation'];
        delete vm.params['skills'];
      }

      if (vm.tribeFilter) {
        vm.params.tribe = vm.tribeFilter;
      }


      let searchParams = new URLSearchParams(vm.params);

      let apiUrlUsers = `/api/v0.1/users_fetch/?${searchParams.toString()}`;

      if (vm.hideFilterButton) {
        apiUrlUsers += '&type=explore_tribes';
      }

      var getUsers = fetchData(apiUrlUsers, 'GET');

      $.when(getUsers).then(function(response) {

        response.data.forEach(function(item) {
          vm.users.push(item);
        });

        vm.usersNumPages = response.num_pages;
        vm.usersHasNext = response.has_next;
        vm.numUsers = response.count;
        vm.showBanner = response.show_banner;
        vm.persona = response.persona;
        vm.rating = response.rating;
        if (vm.usersHasNext) {
          vm.usersPage = ++vm.usersPage;

        } else {
          vm.usersPage = 1;
        }

        if (vm.users.length) {
          vm.noResults = false;
        } else {
          vm.noResults = true;
        }
        vm.isLoading = false;
      });
    },
    searchUsers: function() {
      let vm = this;

      vm.users = [];

      vm.fetchUsers(1);

    },
    bottomVisible: function() {
      let vm = this;

      const scrollY = window.scrollY;
      const visible = document.documentElement.clientHeight;
      const pageHeight = document.documentElement.scrollHeight - 500;
      const bottomOfPage = visible + scrollY >= pageHeight;

      if (bottomOfPage || pageHeight < visible) {
        if (vm.usersHasNext) {
          vm.fetchUsers();
          vm.usersHasNext = false;
        }
      }
    },
    fetchBounties: function() {
      let vm = this;

      // fetch bounties
      let apiUrlBounties = '/api/v0.1/user_bounties/';

      let getBounties = fetchData(apiUrlBounties, 'GET');

      $.when(getBounties).then((response) => {
        vm.isFunder = response.is_funder;
        vm.funderBounties = response.data;
      });

    },
    openBounties: function(user) {
      let vm = this;

      vm.userSelected = user;
    },
    sendInvite: function(bounty, user) {
      let vm = this;

      console.log(vm.bountySelected, bounty, user, csrftoken);
      let apiUrlInvite = '/api/v0.1/social_contribution_email/';
      let postInvite = fetchData(
        apiUrlInvite,
        'POST',
        {'usersId': [user], 'bountyId': bounty.id},
        {'X-CSRFToken': csrftoken}
      );

      $.when(postInvite).then((response) => {
        console.log(response);
        if (response.status === 500) {
          _alert(response.msg, 'error');

        } else {
          vm.$refs['user-modal'].closeModal();
          _alert('The invitation has been sent', 'info');
        }
      });
    },
    sendInviteAll: function(bountyUrl) {
      let vm = this;
      const apiUrlInvite = '/api/v0.1/bulk_invite/';
      const postInvite = fetchData(
        apiUrlInvite,
        'POST',
        {'params': vm.params, 'bountyId': bountyUrl},
        {'X-CSRFToken': csrftoken}
      );

      $.when(postInvite).then((response) => {
        console.log(response);
        if (response.status !== 200) {
          _alert(response.msg, 'error');

        } else {
          vm.$refs['user-modal'].closeModal();
          _alert('The invitation has been sent', 'info');
        }
      });

    },
    getIssueDetails: function(url) {
      let vm = this;
      const apiUrldetails = `/actions/api/v0.1/bounties/?github_url=${encodeURIComponent(url)}`;

      vm.errorIssueDetails = undefined;

      if (url.indexOf('github.com/') < 0) {
        vm.issueDetails = null;
        vm.errorIssueDetails = 'Please paste a github issue url';
        return;
      }
      vm.issueDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        if (response[0]) {
          vm.issueDetails = response[0];
          vm.errorIssueDetails = undefined;
        } else {
          vm.issueDetails = null;
          vm.errorIssueDetails = 'This issue wasn\'t bountied yet.';
        }
      });

    },
    closeModal() {
      this.$refs['user-modal'].closeModal();
    },
    inviteOnMount: function() {
      let vm = this;

      vm.contributorInvite = getURLParams('invite');
      vm.currentBounty = getURLParams('current-bounty');

      if (vm.contributorInvite) {
        let api = `/api/v0.1/users_fetch/?search=${vm.contributorInvite}`;
        let getUsers = fetchData(api, 'GET');

        $.when(getUsers).then(function(response) {
          if (response && response.data.length) {
            vm.openBounties(response.data[0]);
            $('#userModal').bootstrapModal('show');
          } else {
            _alert('The user was not found. Please try using the search box.', 'error');
          }
        });
      }
    },
    extractURLFilters: function() {
      let vm = this;
      let params = getURLParams();

      vm.users = [];

      if (params) {
        for (var prop in params) {
          if (prop === 'skills') {
            vm.$set(vm.params, prop, params[prop].split(','));
          } else {
            vm.$set(vm.params, prop, params[prop]);
          }
        }
      }
    },
    joinTribe: function(user, event) {
      event.target.disabled = true;
      const url = `/tribe/${user.handle}/join/`;
      const sendJoin = fetchData(url, 'POST', {}, {'X-CSRFToken': csrftoken});

      $.when(sendJoin).then(function(response) {
        event.target.disabled = false;

        if (response.is_member) {
          ++user.follower_count;
          user.is_following = true;
        } else {
          --user.follower_count;
          user.is_following = false;
        }

        event.target.classList.toggle('btn-outline-green');
        event.target.classList.toggle('btn-gc-blue');
      }).fail(function(error) {
        event.target.disabled = false;
      });
    }
  }
});
Vue = Vue.extend({
  delimiters: [ '[[', ']]' ]
});


Vue.component('directory-card', {
  name: 'DirectoryCard',
  delimiters: [ '[[', ']]' ],
  props: [ 'user', 'funderBounties' ]
});
Vue.use(innerSearch.default);
Vue.component('autocomplete', {
  props: [ 'options', 'value' ],
  template: '#select2-template',
  methods: {
    formatMapping: function(item) {
      console.log(item);
      return item.name;
    },
    formatMappingSelection: function(filter) {
      return '';
    }
  },
  mounted() {
    let count = 0;
    let vm = this;

    let data = $.map(this.options, function(obj, key) {
      obj.id = count++;
      obj.text = key;
      return obj;
    });


    $(vm.$el).select2({
      data: data,
      multiple: true,
      allowClear: true,
      placeholder: 'Search for another filter to add',
      minimumInputLength: 1,
      templateSelection: this.formatSelection,
      escapeMarkup: function(markup) {
        return markup;
      }
    })
      .on('change', function() {
        console.log('changed');
        let val = $(vm.$el).val();

        let changeData = $.map(val, function(filter) {
          return data[filter];
        });

        vm.$emit('input', changeData);
      });

    // fix for wrong position on select open
    var select2Instance = $(vm.$el).data('select2');

    select2Instance.on('results:message', function(params) {
      this.dropdown._resizeDropdown();
      this.dropdown._positionDropdown();
    });
  },
  destroyed: function() {
    $(this.$el).off().select2('destroy');
    this.$emit('destroyed');
  }
});
Vue.component('user-directory', {
  delimiters: [ '[[', ']]' ],
  props: [ 'tribe', 'is_my_org' ],
  data: function() {
    return {
      orgOwner: this.is_my_org || false,
      userFilter: {
        options: [
          {text: 'All', value: 'all'},
          {text: 'Tribe Owners', value: 'owners'},
          {text: 'Tribe Members', value: 'members'},
          {text: 'Tribe Hackers', value: 'hackers'}
        ]
      },
      tribeFilter: this.tribe || '',
      users,
      usersPage,
      hackathonId,
      usersNumPages,
      usersHasNext,
      numUsers,
      media_url,
      chatURL: document.chatURL || 'https://chat.gitcoin.co/',
      searchTerm: null,
      bottom: false,
      params: {
        'user_filter': 'all'
      },
      funderBounties: [],
      currentBounty: undefined,
      contributorInvite: undefined,
      isFunder: false,
      bountySelected: null,
      userSelected: [],
      showModal: false,
      showFilters: true,
      skills: document.keywords,
      selectedSkills: [],
      noResults: false,
      isLoading: true,
      gitcoinIssueUrl: '',
      issueDetails: undefined,
      errorIssueDetails: undefined,
      showBanner: undefined,
      persona: undefined,
      hideFilterButton: !!document.getElementById('explore_tribes'),
      expandFilter: true
    };
  },

  mounted() {
    this.fetchUsers();
    this.tribeFilter = this.tribe;
    this.$watch('params', function(newVal, oldVal) {
      this.searchUsers();
    }, {
      deep: true
    });
  },
  created() {
    if (document.contxt.github_handle && this.is_my_org) {
      this.fetchBounties();
    }
    this.inviteOnMount();
    this.extractURLFilters();
  },
  beforeMount() {
    if (this.isMobile) {
      this.showFilters = false;
    }
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    }, false);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    });
  }
});
Vue.component('user-directory-elastic', {
  delimiters: [ '[[', ']]' ],
  data: function() {
    return {
      filters: [],
      esColumns: [],
      filterLoaded: false,
      users,
      usersPage,
      usersNumPages,
      usersHasNext,
      numUsers,
      media_url,
      chatURL: document.chatURL || 'https://chat.gitcoin.co/',
      searchTerm: null,
      bottom: false,
      params: {},
      funderBounties: [],
      currentBounty: undefined,
      contributorInvite: undefined,
      isFunder: false,
      bountySelected: null,
      userSelected: [],
      showModal: false,
      showFilters: !document.getElementById('explore_tribes'),
      skills: document.keywords,
      selectedSkills: [],
      noResults: false,
      isLoading: true,
      gitcoinIssueUrl: '',
      issueDetails: undefined,
      errorIssueDetails: undefined,
      showBanner: undefined,
      persona: undefined,
      hideFilterButton: !!document.getElementById('explore_tribes')
    };
  },
  methods: {
    autoCompleteDestroyed: function() {
      this.filters = [];
    },
    autoCompleteChange: function(filters) {
      this.filters = filters;
    },
    outputToCSV: function() {
      let url = '/api/v0.1/users_csv/';

      $.get(url, this.body).then(resp => resp.json()).then(json => {
        _alert(json.message);
      }).catch(() => _alert('There was an issue processing your request'));
    },
    fetchMappings: function() {
      let vm = this;

      $.when(vm.header.client.indices.getMapping())
        .then(response => {
          vm.esColumns = response[vm.header.index]['mappings'][vm.header.type]['properties'];
          vm.filterLoaded = true;
        });
    }
  },
  mounted() {
    this.fetchMappings();
    // this.fetchUsers();
    this.$watch('params', function(newVal, oldVal) {
      this.searchUsers();
    }, {
      deep: true
    });
  },
  created() {
    this.setHost(document.contxt.search_url);
    this.setIndex('haystack');
    this.setType('modelresult');
    this.fetchBounties();
    this.inviteOnMount();
    this.extractURLFilters();
  },
  beforeMount() {
    window.addEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    }, false);
  },
  beforeDestroy() {
    window.removeEventListener('scroll', () => {
      this.bottom = this.bottomVisible();
    });
  }
});
if (document.getElementById('gc-users-elastic')) {

  window.UserDirectory = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-users-elastic',
    data: {
      csrf: document.csrf,
      filters: [],
      esColumns: [],
      filterLoaded: false,
      users,
      usersPage,
      usersNumPages,
      usersHasNext,
      numUsers,
      media_url,
      chatURL: document.chatURL || 'https://chat.gitcoin.co/',
      searchTerm: null,
      bottom: false,
      params: {},
      funderBounties: [],
      currentBounty: undefined,
      contributorInvite: undefined,
      isFunder: false,
      bountySelected: null,
      userSelected: [],
      showModal: false,
      showFilters: !document.getElementById('explore_tribes'),
      skills: document.keywords,
      selectedSkills: [],
      noResults: false,
      isLoading: true,
      gitcoinIssueUrl: '',
      issueDetails: undefined,
      errorIssueDetails: undefined,
      showBanner: undefined,
      persona: undefined,
      hideFilterButton: !!document.getElementById('explore_tribes')
    },
    methods: {
      resetCallback: function() {
        this.checkedItems = [];
      },
      autoCompleteDestroyed: function() {
        this.filters = [];
      },
      autoCompleteChange: function(filters) {
        this.filters = filters;
      },
      outputToCSV: function() {

        let url = '/api/v0.1/users_csv/';

        const csvRequest = fetchData(url, 'POST', JSON.stringify(this.body), {'X-CSRFToken': vm.csrf, 'Content-Type': 'application/json;'});

        $.when(csvRequest).then(json => {
          _alert(json.message);
        }).catch(() => _alert('There was an issue processing your request'));
      },

      fetchMappings: function() {
        let vm = this;

        $.when(vm.header.client.indices.getMapping())
          .then(response => {
            vm.esColumns = response[vm.header.index]['mappings'][vm.header.type]['properties'];
            vm.filterLoaded = true;
          });
      }
    },
    mounted() {
      this.fetchMappings();
      this.fetch(this);
      this.$watch('params', function(newVal, oldVal) {
        this.searchUsers();
      }, {
        deep: true
      });
    },
    created() {
      this.setHost(document.contxt.search_url);
      this.setIndex('haystack');
      this.setType('modelresult');

      // this.extractURLFilters();
    },
    beforeMount() {
      window.addEventListener('scroll', () => {
        this.bottom = this.bottomVisible();
      }, false);
    },
    beforeDestroy() {
      window.removeEventListener('scroll', () => {
        this.bottom = this.bottomVisible();
      });
    }
  });
}
