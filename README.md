# Hi, I'm jps4242 👋

`developer.js`:
```javascript
class Developer {
    constructor(name, info) {
        this.name = name;
        this.info = info;
    }

    sayHello() {
        console.log(
            `Hi 👋, I'm ${this.name}, a passionate full-stack developer and sysadmin!`
        );
    }
}

const jps4242 = new Developer('jps4242', {
    languages: [
        'Python', 'JavaScript', 'TypeScript', 'HTML', 'CSS', 'SQL'
    ],
    interests: [
        'Building useful software',
        'Learning new technologies',
        'Solving interesting problems'
    ],
    technologies: {
        frontend: ['Vue.js', 'Vite'],
        backend: ['FastAPI', 'Node.js'],
        data: {
            databases: ['PostgreSQL', 'Redis', 'SQLite'],
            storage: ['MinIO']
        },
        tools: [
            'Linux', 'Docker', 'Podman', 'VS Code', 'GitHub', 'Gitea', 'Git'
        ],
    }
});
jps4242.sayHello();
```

```bash
hello@jps4242:~ $ node ./developer.js
Hi 👋, I'm jps4242, a passionate full-stack developer and sysadmin!
```

I'm a full stack developer interested in building useful software, learning new technologies, and solving interesting problems.

## Projects I maintain

- [Seekra](https://github.com/seekra-se) – An open-source search engine (GitHub organization is a mirror)
- [jCloud](https://gitea.jcloud-services.ddns.net/jCloud) – Open-source cloud ecosystem

## GitHub Stats

![jps4242's GitHub stats](https://github-readme-stats.vercel.app/api?username=jps4242&show_icons=true&theme=dark)

## Connect

- [GitHub](https://github.com/jps4242)
- [jCloud Gitea](https://gitea.jcloud-services.ddns.net/jakob.scheid)
